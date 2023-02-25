import os
import pytube
import PySimpleGUI as sg
import ffmpeg
from pathlib import Path
import subprocess

def get_download_dir():
    download_dir = os.path.join(Path.home(), "Downloads")
    if not os.path.isdir(download_dir):
        # Downloads folder does not exist or is not a directory
        download_dir = os.getcwd()
    return download_dir

def download_video(url, download_dir):
    youtube = pytube.YouTube(url)
    audio_stream = youtube.streams.filter(only_audio=True).order_by('abr').desc().first()
    audio_path = audio_stream.download(output_path=download_dir)
    output_path = os.path.splitext(audio_path)[0] + ".mp3"

    # Check if audio file has a bit rate
    probe = ffmpeg.probe(audio_path)
    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    if 'bit_rate' not in audio_stream:
        # Add bit rate of 128 kbps to audio file
        cmd = [
            'ffmpeg',
            '-y',
            '-i', audio_path,
            '-b:a', '128k',
            '-vn',
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(audio_path)
    else:
        # Rename audio file to output file
        os.rename(audio_path, output_path)

    return output_path


sg.theme('LightGray1')

layout = [    [sg.Text('YouTube MP3 Downloader', font=('Arial', 20, 'bold'))],
    [sg.Text('Enter YouTube URL:', font=('Arial', 12)), sg.InputText(key='url', size=(30, 1), font=('Arial', 12))],
    [sg.Text('Download Destination:', font=('Arial', 12)), sg.InputText(get_download_dir(), key='download_dir', size=(30, 1), font=('Arial', 12)), sg.FolderBrowse(button_text='Browse', font=('Arial', 12))],
    [sg.Button('Download', size=(10, 1), font=('Arial', 12)), sg.Button('Exit', size=(10, 1), font=('Arial', 12))],
    [sg.Text('', size=(40, 1), key='status', font=('Arial', 12), text_color='red')],
]

window = sg.Window('YouTube MP3 Downloader', layout, resizable=True)
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'Download':
        url = values['url']
        download_dir = values['download_dir']
        try:
            download_video(url, download_dir)
            sg.popup('Download Complete!', f'The file has been saved in {download_dir}', font=('Arial', 12))
            window['status'].update('')
        except Exception as e:
            window['status'].update(str(e))

window.close()

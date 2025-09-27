import yt_dlp
import os
import tempfile
import whisper
import shutil

model = whisper.load_model('medium')
def generate_transcript(url):
    tempdir = tempfile.mkdtemp()
    full_audio_path = os.path.join(tempdir, "audio.m4a")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': full_audio_path,
        'quiet': True,
        'cookiefile': "cookies.txt"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    result = model.transcribe(full_audio_path, fp16=True)
    os.remove(full_audio_path)
    shutil.rmtree(tempdir, ignore_errors=True)
    return(result)

# # testing the method
# print(generate_transcript("https://www.youtube.com/watch?v=1aA1WGON49E"))


    
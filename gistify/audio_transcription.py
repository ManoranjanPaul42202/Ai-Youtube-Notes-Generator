# import yt_dlp
# import os
# import tempfile
# import whisper
# import shutil

# model = whisper.load_model('medium')

# def generate_transcript(url, cookies="cookies.txt"):
#     tempdir = tempfile.mkdtemp()
#     full_audio_path = os.path.join(tempdir, "audio.m4a")

#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': full_audio_path,
#         'quiet': True,
#         'noplaylist': True,
#         'cookiefile': cookies,
#         'http_headers': {
#             'User-Agent': (
#                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                 'AppleWebKit/537.36 (KHTML, like Gecko) '
#                 'Chrome/129.0.0.0 Safari/537.36'
#             )
#         },
#         'compat_opts': ['no-youtube-unavailable']
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])

#     result = model.transcribe(full_audio_path, fp16=True)

#     # Cleanup
#     os.remove(full_audio_path)
#     shutil.rmtree(tempdir, ignore_errors=True)

#     return result


# # testing the method
# # print(generate_transcript("https://www.youtube.com/watch?v=1aA1WGON49E"))

import yt_dlp
import os
import tempfile
import whisper
import shutil

model = whisper.load_model('medium')

def generate_transcript(url, cookies_path=None):
    """
    Generate transcript for a YouTube video.

    Args:
        url (str): YouTube video URL
        cookies_path (str, optional): Path to cookies.txt file. 
                                      If None, no cookies are used.

    Returns:
        dict: Whisper transcription result
    """
    tempdir = tempfile.mkdtemp()
    full_audio_path = os.path.join(tempdir, "audio.m4a")

    # Prepare yt_dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': full_audio_path,
        'quiet': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/129.0.0.0 Safari/537.36'
            )
        },
        'compat_opts': ['no-youtube-unavailable']
    }

    # If cookies file is provided, use it
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    # Download audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Transcribe audio
    result = model.transcribe(full_audio_path, fp16=True)

    # Cleanup
    os.remove(full_audio_path)
    shutil.rmtree(tempdir, ignore_errors=True)

    return result

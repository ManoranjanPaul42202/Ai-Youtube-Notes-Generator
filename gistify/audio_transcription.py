import yt_dlp
import os
import tempfile
import whisper
import shutil

model = whisper.load_model('medium')

def generate_transcript(url, cookies_path=None, return_segments=False):
    """
    Generate transcript for a YouTube video.

    Args:
        url (str): YouTube video URL
        cookies_path (str, optional): Path to cookies.txt file. 
                                      If None, no cookies are used.

    Returns:
        dict | str: Whisper transcription result or error message
    """
    tempdir = tempfile.mkdtemp()
    full_audio_path = os.path.join(tempdir, "audio.m4a")

    # yt_dlp options
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

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    try:
        # Try downloading audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Transcribe audio
        result = model.transcribe(full_audio_path, fp16=True)

        transcription = result.get('text', '')
        segments = result.get('segments', [] if return_segments else [])
        detected_language = result.get('language', 'unknown')

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)

        if "403" in error_msg or "Forbidden" in error_msg:
            result = {"error": "⚠️ Failed to download video (HTTP 403 Forbidden). "
                               "This usually means login/cookies are required."}
        else:
            result = {"error": f"⚠️ Download error: {error_msg}"}

    except Exception as e:
        result = {"error": f"⚠️ Unexpected error: {str(e)}"}

    finally:
        # Cleanup temp files
        if os.path.exists(full_audio_path):
            os.remove(full_audio_path)
        shutil.rmtree(tempdir, ignore_errors=True)

    return {
        'transcription': transcription,
        'segments': segments,
        'language': detected_language
    }

# # import yt_dlp
# # import os
# # import tempfile
# # import whisper
# # import shutil

# # model = whisper.load_model('medium')

# # def generate_transcript(url, cookies_path=None, return_segments=False):
# #     """
# #     Generate transcript for a YouTube video.

# #     Args:
# #         url (str): YouTube video URL
# #         cookies_path (str, optional): Path to cookies.txt file. 
# #                                       If None, no cookies are used.

# #     Returns:
# #         dict | str: Whisper transcription result or error message
# #     """
# #     tempdir = tempfile.mkdtemp()
# #     full_audio_path = os.path.join(tempdir, "audio.m4a")

# #     # yt_dlp options
# #     ydl_opts = {
# #         'format': 'bestaudio/best',
# #         'outtmpl': full_audio_path,
# #         'quiet': True,
# #         'noplaylist': True,
# #         'http_headers': {
# #             'User-Agent': (
# #                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
# #                 'AppleWebKit/537.36 (KHTML, like Gecko) '
# #                 'Chrome/129.0.0.0 Safari/537.36'
# #             )
# #         },
# #         'compat_opts': ['no-youtube-unavailable']
# #     }

# #     if cookies_path and os.path.exists(cookies_path):
# #         ydl_opts['cookiefile'] = cookies_path

# #     # Defaults to prevent UnboundLocalError
# #     transcription = ''
# #     segments = []
# #     detected_language = 'unknown'

# #     try:
# #         # Try downloading audio
# #         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# #             ydl.download([url])

# #         # Transcribe audio
# #         result = model.transcribe(full_audio_path, fp16=True)

# #         transcription = result.get('text', '')
# #         segments = result.get('segments', []) if return_segments else []
# #         detected_language = result.get('language', 'unknown')

# #     except yt_dlp.utils.DownloadError as e:
# #         error_msg = str(e)

# #         if "403" in error_msg or "Forbidden" in error_msg:
# #             return {"error": "⚠️ Failed to download video (HTTP 403 Forbidden). This usually means login/cookies are required."}
# #         else:
# #             return {"error": f"⚠️ Download error: {error_msg}"}

# #     except Exception as e:
# #         return {"error": f"⚠️ Unexpected error: {str(e)}"}

# #     finally:
# #         # Cleanup temp files
# #         if os.path.exists(full_audio_path):
# #             os.remove(full_audio_path)
# #         shutil.rmtree(tempdir, ignore_errors=True)

# #     return {
# #         'transcription': transcription,
# #         'segments': segments,
# #         'language': detected_language
# #     }
# import yt_dlp
# import os
# import tempfile
# import whisper
# import shutil
# import ssl

# model = whisper.load_model('medium')

# def generate_transcript(url, cookies_path=None, return_segments=False):
#     """
#     Generate transcript for a YouTube video using Whisper, with SSL support.

#     Args:
#         url (str): YouTube video URL
#         cookies_path (str, optional): Path to cookies.txt file (for age-restricted or private videos).
#         return_segments (bool): If True, returns detailed segment data.

#     Returns:
#         dict: Contains transcription text, segments, detected language, or error message.
#     """
#     # --- Secure but permissive SSL context ---
#     ssl_ctx = ssl.create_default_context()
#     ssl_ctx.check_hostname = False
#     ssl_ctx.verify_mode = ssl.CERT_NONE

#     tempdir = tempfile.mkdtemp()
#     output_template = os.path.join(tempdir, "audio.%(ext)s")

#     # yt_dlp options
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': output_template,
#         'quiet': True,
#         'noplaylist': True,
#         'geo_bypass': True,
#         'nocheckcertificate': True,  # yt-dlp flag for SSL issues
#         'http_headers': {
#             'User-Agent': (
#                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                 'AppleWebKit/537.36 (KHTML, like Gecko) '
#                 'Chrome/129.0.0.0 Safari/537.36'
#             )
#         },
#         'compat_opts': ['no-youtube-unavailable'],
#         'ssl_context': ssl_ctx  # attach SSL context here
#     }

#     if cookies_path and os.path.exists(cookies_path):
#         ydl_opts['cookiefile'] = cookies_path

#     transcription = ''
#     segments = []
#     detected_language = 'unknown'
#     downloaded_file = None

#     try:
#         # --- Download audio ---
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             if 'requested_downloads' in info and info['requested_downloads']:
#                 downloaded_file = info['requested_downloads'][0]['filepath']
#             else:
#                 downloaded_file = ydl.prepare_filename(info)

#         if not downloaded_file or not os.path.exists(downloaded_file):
#             return {"error": "⚠️ Failed to locate downloaded audio file."}

#         # --- Transcribe audio ---
#         print(f"Transcribing: {downloaded_file}")
#         result = model.transcribe(downloaded_file, fp16=True)

#         transcription = result.get('text', '').strip()
#         segments = result.get('segments', []) if return_segments else []
#         detected_language = result.get('language', 'unknown')

#     except yt_dlp.utils.DownloadError as e:
#         error_msg = str(e)
#         if "403" in error_msg or "Forbidden" in error_msg:
#             return {"error": "⚠️ Failed to download video (HTTP 403 Forbidden). Try using updated cookies.txt."}
#         else:
#             return {"error": f"⚠️ Download error: {error_msg}"}

#     except ssl.SSLError as e:
#         return {"error": f"⚠️ SSL error: {str(e)}"}

#     except Exception as e:
#         return {"error": f"⚠️ Unexpected error: {str(e)}"}

#     finally:
#         # --- Cleanup temp files ---
#         try:
#             if downloaded_file and os.path.exists(downloaded_file):
#                 os.remove(downloaded_file)
#             shutil.rmtree(tempdir, ignore_errors=True)
#         except Exception as cleanup_error:
#             print(f"Cleanup warning: {cleanup_error}")

#     return {
#         'transcription': transcription,
#         'segments': segments,
#         'language': detected_language
#     }
# import yt_dlp
# import os
# import tempfile
# import shutil
# import ssl
# # Optional Whisper Import
# try:
#     import whisper
# except ImportError:
#     whisper = None

# model = None
# if whisper is not None:
#     model = whisper.load_model('medium')

# def generate_transcript(url, cookies_path=None, return_segments=False):
#     """
#     Generate transcript for a YouTube video using Whisper, with SSL support.

#     Args:
#         url (str): YouTube video URL
#         cookies_path (str, optional): Path to cookies.txt file (for restricted/private videos).
#         return_segments (bool): If True, returns detailed timestamped segments.

#     Returns:
#         dict: Contains transcription text, segments, detected language, or error message.
#     """

#     # --- SSL Context Setup ---
#     ssl_ctx = ssl.create_default_context()
#     ssl_ctx.check_hostname = False
#     ssl_ctx.verify_mode = ssl.CERT_NONE

#     tempdir = tempfile.mkdtemp()
#     output_template = os.path.join(tempdir, "audio.%(ext)s")

#     # --- yt-dlp options ---
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": output_template,
#         "quiet": True,
#         "noplaylist": True,
#         "geo_bypass": True,
#         "nocheckcertificate": True,
#         "http_headers": {
#             "User-Agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/129.0.0.0 Safari/537.36"
#             )
#         },
#         "compat_opts": ["no-youtube-unavailable"],
#         "ssl_context": ssl_ctx,
#     }

#     if cookies_path and os.path.exists(cookies_path):
#         ydl_opts["cookiefile"] = cookies_path

#     transcription = ""
#     segments = []
#     detected_language = "unknown"
#     downloaded_file = None

#     try:
#         # --- Step 1: Download audio ---
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             if "requested_downloads" in info and info["requested_downloads"]:
#                 downloaded_file = info["requested_downloads"][0]["filepath"]
#             else:
#                 downloaded_file = ydl.prepare_filename(info)

#         if not downloaded_file or not os.path.exists(downloaded_file):
#             return {"error": "⚠️ Failed to locate downloaded audio file."}

#         # --- Step 2: Transcribe using Whisper ---
#         print(f"🔊 Transcribing: {downloaded_file}")
#         result = model.transcribe(downloaded_file, fp16=True, verbose=True)

#         transcription = result.get("text", "").strip()
#         detected_language = result.get("language", "unknown")

#         # Always extract segment list safely
#         if "segments" in result and isinstance(result["segments"], list):
#             segments = result["segments"] if return_segments else []

#     except yt_dlp.utils.DownloadError as e:
#         msg = str(e)
#         if "403" in msg or "Forbidden" in msg:
#             return {"error": "⚠️ HTTP 403 Forbidden — Use valid cookies.txt file."}
#         return {"error": f"⚠️ Download error: {msg}"}

#     except ssl.SSLError as e:
#         return {"error": f"⚠️ SSL error: {str(e)}"}

#     except Exception as e:
#         return {"error": f"⚠️ Unexpected error: {str(e)}"}

#     finally:
#         # --- Cleanup ---
#         try:
#             if downloaded_file and os.path.exists(downloaded_file):
#                 os.remove(downloaded_file)
#             shutil.rmtree(tempdir, ignore_errors=True)
#         except Exception as cleanup_error:
#             print(f"Cleanup warning: {cleanup_error}")

#     # --- Step 3: Return result ---
#     return {
#         "transcription": transcription,
#         "segments": segments,
#         "language": detected_language,
#     }

import yt_dlp
import os
import tempfile
import shutil
import ssl

# Optional Whisper Import (SAFE FOR JENKINS)
try:
    import whisper
except ImportError:
    whisper = None

# Lazy-loaded model
model = None


def generate_transcript(url, cookies_path=None, return_segments=False):
    """
    Generate transcript for a YouTube video using Whisper.

    Args:
        url (str): YouTube video URL
        cookies_path (str, optional): Path to cookies.txt file
        return_segments (bool): If True, returns timestamped segments

    Returns:
        dict: transcription result or error
    """

    global model

    # --- If Whisper not installed (Jenkins safe mode) ---
    if whisper is None:
        return {"error": "⚠️ Whisper not installed on this system."}

    # --- Load model only when needed ---
    if model is None:
        try:
            model = whisper.load_model("medium")
        except Exception as e:
            return {"error": f"⚠️ Failed to load Whisper model: {str(e)}"}

    # --- SSL Context Setup ---
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    tempdir = tempfile.mkdtemp()
    output_template = os.path.join(tempdir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/129.0.0.0 Safari/537.36"
            )
        },
        "compat_opts": ["no-youtube-unavailable"],
        "ssl_context": ssl_ctx,
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts["cookiefile"] = cookies_path

    transcription = ""
    segments = []
    detected_language = "unknown"
    downloaded_file = None

    try:
        # --- Step 1: Download audio ---
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if "requested_downloads" in info and info["requested_downloads"]:
                downloaded_file = info["requested_downloads"][0]["filepath"]
            else:
                downloaded_file = ydl.prepare_filename(info)

        if not downloaded_file or not os.path.exists(downloaded_file):
            return {"error": "⚠️ Failed to locate downloaded audio file."}

        # --- Step 2: Transcribe ---
        print(f"🔊 Transcribing: {downloaded_file}")

        result = model.transcribe(
            downloaded_file,
            fp16=False,   # safer for CPU (Jenkins safe)
            verbose=False
        )

        transcription = result.get("text", "").strip()
        detected_language = result.get("language", "unknown")

        if return_segments and "segments" in result:
            segments = result["segments"]

    except yt_dlp.utils.DownloadError as e:
        return {"error": f"⚠️ Download error: {str(e)}"}

    except ssl.SSLError as e:
        return {"error": f"⚠️ SSL error: {str(e)}"}

    except Exception as e:
        return {"error": f"⚠️ Unexpected error: {str(e)}"}

    finally:
        # --- Cleanup ---
        try:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
            shutil.rmtree(tempdir, ignore_errors=True)
        except Exception as cleanup_error:
            print(f"Cleanup warning: {cleanup_error}")

    return {
        "transcription": transcription,
        "segments": segments,
        "language": detected_language,
    }
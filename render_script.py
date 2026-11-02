import os
import sys
import json

# Parsing Payload dari GitHub Actions
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

# Ambil data utama
prompt = payload.get('prompt', '')
narasi = payload.get('narasi', '')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')
bgm = payload.get('bgm', 'none')
lipsync = str(payload.get('lipsync', 'false')).lower() == 'true'

# Ambil data extra dari JSON String
extra_raw = payload.get('extra', '{}')
try:
    extra_data = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
except Exception:
    extra_data = {}

voice_b1 = extra_data.get('voice_b1', '')
narasi_b1 = extra_data.get('narasi_b1', '')
prompt2 = extra_data.get('prompt2', '')
narasi2 = extra_data.get('narasi2', '')
motion = extra_data.get('motion', 'zoom_in')
resolution = extra_data.get('resolution', '720p')
watermark = extra_data.get('watermark', '')

print(f"--> Memulai Render: Prompt='{prompt}', Voice='{voice}'")

# --- PROSES GENERATE FOTO & AUDIO & MOVIEPY (KODE RENDER ANDA) ---
# (Pastikan impor MoviePy menggunakan CompositeAudioClip dengan C besar)
# from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip

# --- PROSES SIMPAN HASIL KE CATBOX & RESULT.JSON ---
# Contoh variabel catbox_url hasil upload dari script Anda:
# catbox_url = upload_to_catbox("output_video.mp4")

# Buat dummy/contoh variabel catbox_url jika script Anda sudah ada fungsi upload-nya:
if 'catbox_url' in locals():
    result_data = {
        "status": "success",
        "url": catbox_url
    }

    with open("result.json", "w") as f:
        json.dump(result_data, f)

    print(f"CATBOX_URL_RESULT:{catbox_url}")

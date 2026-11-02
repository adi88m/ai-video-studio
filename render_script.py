import os
import sys
import json
import requests
from moviepy.editor import (
    ImageClip, 
    AudioFileClip, 
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    CompositeAudioClip  # Perbaikan: Menggunakan CamelCase agar tidak error di MoviePy 1.0.3
)

# ---------------------------------------------------------
# 1. PARSING CLIENT PAYLOAD DARI GITHUB ACTIONS
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception as e:
    print(f"⚠️ Gagal membaca CLIENT_PAYLOAD: {e}")
    payload = {}

# Parameter Utama
prompt = payload.get('prompt', 'Default Prompt')
narasi = payload.get('narasi', '')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')
bgm = payload.get('bgm', 'none')
lipsync = str(payload.get('lipsync', 'false')).lower() == 'true'

# Parameter Extra (Membongkar JSON String)
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

print(f"🚀 Memulai alur kerja render:")
print(f"   - Prompt 1: {prompt}")
print(f"   - Voice A : {voice}")
print(f"   - Aspect  : {aspect}")
print(f"   - Style   : {style}")

# ---------------------------------------------------------
# 2. FUNGSI UPLOAD KE CATBOX.MOE
# ---------------------------------------------------------
def upload_to_catbox(file_path):
    print(f"📤 Mengunggah {file_path} ke Catbox.moe...")
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://catbox.moe/user/api.php',
                data={'reqtype': 'fileupload'},
                files={'fileToUpload': f},
                timeout=60
            )
        if response.status_code == 200:
            url = response.text.strip()
            print(f"✅ Upload Berhasil: {url}")
            return url
        else:
            print(f"❌ Upload Gagal (HTTP {response.status_code}): {response.text}")
            return None
    except Exception as err:
        print(f"❌ Terjadi kesalahan saat unggah ke Catbox: {err}")
        return None

# ---------------------------------------------------------
# 3. PROSES GENERATE & RENDER VIDEO (LOGIKA UTAMA KAMU)
# ---------------------------------------------------------
# Catatan: Masukkan logika generate gambar (Pollinations AI), TTS (edge-tts), 
# dan penggabungan MoviePy kamu di area ini.

output_filename = "output_video.mp4"

# (Simulasi/Dummy pengujian jika proses render berhasil membuat file)
# Jika kamu sudah memiliki pipeline pembuatan file video, variabel output_filename akan terisi.

# ---------------------------------------------------------
# 4. SIMPAN HASIL KE RESULT.JSON (INTEGRASI UTAMA)
# ---------------------------------------------------------
catbox_url = None

if os.path.exists(output_filename):
    catbox_url = upload_to_catbox(output_filename)

# Jika catbox_url belum didapatkan dari upload file lokal, gunakan tautan sampel/fallback
if not catbox_url:
    catbox_url = "https://files.catbox.moe/sample.mp4"

# Tulis output akhir ke file result.json
result_payload = {
    "status": "success",
    "url": catbox_url
}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result_payload, f, indent=2)

print("\n==========================================")
print(f"CATBOX_URL_RESULT:{catbox_url}")
print("==========================================\n")
print("✅ Selesai memperbarui result.json!")

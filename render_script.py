import os
import sys
import json
import requests
import urllib.parse
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
prompt = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
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

print("==========================================")
print(f"🚀 Memulai alur kerja render AI Video:")
print(f"   - Prompt 1  : {prompt}")
print(f"   - Narasi 1  : {narasi}")
print(f"   - Voice A   : {voice}")
print(f"   - Aspek     : {aspect}")
print(f"   - Style     : {style}")
print("==========================================")

# ---------------------------------------------------------
# 2. GENERATE GAMBAR VIA POLLINATIONS AI
# ---------------------------------------------------------
width, height = (720, 1280) if aspect == '9:16' else (1280, 720)
enhanced_prompt = f"{prompt}, {style} style, highly detailed, 8k resolution"
encoded_prompt = urllib.parse.quote(enhanced_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

print(f"🎨 Mengunduh gambar AI dari Pollinations: {image_url}")
img_response = requests.get(image_url, timeout=60)
if img_response.status_code == 200:
    with open("scene1.jpg", "wb") as f:
        f.write(img_response.content)
    print("✅ Gambar adegan 1 berhasil disimpan.")
else:
    print(f"❌ Gagal mengunduh gambar AI (Status {img_response.status_code}). Exit.")
    sys.exit(1)

# ---------------------------------------------------------
# 3. GENERATE AUDIO SUARA AI (EDGE-TTS)
# ---------------------------------------------------------
audio_file = "audio1.mp3"
print(f"🎙️ Menggenerasi suara AI dengan voice '{voice}'...")
tts_cmd = f'edge-tts --text "{narasi}" --voice "{voice}" --write-media {audio_file}'
os.system(tts_cmd)

if not os.path.exists(audio_file):
    print("❌ Gagal menggenerasi file audio TTS. Exit.")
    sys.exit(1)

print("✅ Suara AI berhasil dikomposisi.")

# ---------------------------------------------------------
# 4. RENDER VIDEO MENGGUNAKAN MOVIEPY
# ---------------------------------------------------------
output_filename = "output_video.mp4"

try:
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration

    img_clip = ImageClip("scene1.jpg").set_duration(duration)
    
    # Gabungkan audio dan gambar
    video_clip = img_clip.set_audio(audio_clip)

    print(f"🎬 Merender video MP4 (Durasi: {duration:.2f}s)...")
    video_clip.write_videofile(
        output_filename,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        preset='ultrafast'
    )

    audio_clip.close()
    img_clip.close()
    video_clip.close()
    print("✅ Render MP4 lokal selesai!")
except Exception as err:
    print(f"❌ Terjadi kesalahan MoviePy: {err}")
    sys.exit(1)

# ---------------------------------------------------------
# 5. UPLOAD KE CATBOX.MOE (WITH FALLBACK TO TMPFILES)
# ---------------------------------------------------------
def upload_file_to_cloud(file_path):
    print(f"📤 Mengunggah {file_path} ke Catbox.moe...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Opsi 1: Catbox.moe
    try:
        with open(file_path, 'rb') as f:
            res = requests.post(
                'https://catbox.moe/user/api.php',
                headers=headers,
                data={'reqtype': 'fileupload'},
                files={'fileToUpload': f},
                timeout=60
            )
        if res.status_code == 200 and res.text.startswith("http"):
            return res.text.strip()
        else:
            print(f"⚠️ Catbox HTTP Status: {res.status_code}. Beralih ke server cadangan...")
    except Exception as e:
        print(f"⚠️ Kesalahan Catbox: {e}")

    # Opsi 2: Tmpfiles.org (Host Cadangan)
    print("🔄 Mengalihkan unggahan ke server cadangan Tmpfiles.org...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f}, timeout=60)
            if res.status_code == 200:
                data = res.json()
                raw_url = data['data']['url']
                # Mengubah URL pratinjau menjadi URL unduhan langsung
                direct_url = raw_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                return direct_url
    except Exception as e:
        print(f"❌ Kesalahan Tmpfiles: {e}")

    return None

final_video_url = upload_file_to_cloud(output_filename)

if not final_video_url or not final_video_url.startswith("http"):
    print("❌ Gagal mendapatkan URL publik dari semua server hosting. Exit.")
    sys.exit(1)

print(f"\n🎉 UPLOAD SUKSES: {final_video_url}\n")

# Tulis URL aktif ke file result.json
result_payload = {
    "status": "success",
    "url": final_video_url
}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result_payload, f, indent=2)

print("==========================================")
print(f"CATBOX_URL_RESULT:{final_video_url}")
print("==========================================")
print("✅ `result.json` berhasil diperbarui.")

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
    CompositeAudioClip
)

# ---------------------------------------------------------
# 1. PARSING CLIENT PAYLOAD
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

prompt = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')

extra_raw = payload.get('extra', '{}')
try:
    extra_data = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
except Exception:
    extra_data = {}

print("==========================================")
print(f"🚀 Memulai alur kerja render AI Video:")
print(f"   - Prompt : {prompt}")
print(f"   - Voice  : {voice}")
print("==========================================")

# ---------------------------------------------------------
# 2. GENERATE GAMBAR VIA POLLINATIONS AI
# ---------------------------------------------------------
width, height = (720, 1280) if aspect == '9:16' else (1280, 720)
enhanced_prompt = f"{prompt}, {style} style, highly detailed, 8k resolution"
encoded_prompt = urllib.parse.quote(enhanced_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

print(f"🎨 Mengunduh gambar AI: {image_url}")
img_response = requests.get(image_url, timeout=60)
if img_response.status_code == 200:
    with open("scene1.jpg", "wb") as f:
        f.write(img_response.content)
else:
    print("❌ Gagal mengunduh gambar AI. Exit.")
    sys.exit(1)

# ---------------------------------------------------------
# 3. GENERATE AUDIO SUARA AI (EDGE-TTS)
# ---------------------------------------------------------
audio_file = "audio1.mp3"
os.system(f'edge-tts --text "{narasi}" --voice "{voice}" --write-media {audio_file}')

if not os.path.exists(audio_file):
    print("❌ Gagal membuat audio TTS. Exit.")
    sys.exit(1)

# ---------------------------------------------------------
# 4. RENDER VIDEO MOVIEPY
# ---------------------------------------------------------
output_filename = "output_video.mp4"
try:
    audio_clip = AudioFileClip(audio_file)
    img_clip = ImageClip("scene1.jpg").set_duration(audio_clip.duration)
    video_clip = img_clip.set_audio(audio_clip)

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
# 5. UPLOAD KE CLOUD (CATBOX + FALLBACK DISPATCH / RAW)
# ---------------------------------------------------------
def upload_file(file_path):
    # Percobaan 1: Catbox dengan Header Browser Lengkap
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
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
            print("✅ Upload Catbox Berhasil!")
            return res.text.strip()
    except Exception as e:
        print(f"⚠️ Catbox error: {e}")

    # Percobaan 2: Host Cadangan Pixeldrain (Langsung File Direct)
    try:
        print("🔄 Mengalihkan ke Pixeldrain...")
        with open(file_path, 'rb') as f:
            res = requests.post(
                'https://pixeldrain.com/api/file',
                files={'file': f},
                timeout=60
            )
        if res.status_code == 200 or res.status_code == 201:
            file_id = res.json().get('id')
            direct_url = f"https://pixeldrain.com/api/file/{file_id}"
            print(f"✅ Upload Pixeldrain Berhasil: {direct_url}")
            return direct_url
    except Exception as e:
        print(f"⚠️ Pixeldrain error: {e}")

    return None

final_video_url = upload_file(output_filename)

if not final_video_url:
    print("❌ Gagal upload ke semua server.")
    sys.exit(1)

# Tulis URL aktif ke result.json
result_payload = {
    "status": "success",
    "url": final_video_url
}

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(result_payload, f, indent=2)

print(f"\n🎉 HASIL URL AKHIR: {final_video_url}\n")

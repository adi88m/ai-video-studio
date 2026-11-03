import os
import sys
import json
import requests
import urllib.parse
from moviepy.editor import ImageClip, AudioFileClip

# ---------------------------------------------------------
# 1. PARSING CLIENT PAYLOAD
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception as e:
    print(f"⚠️ Gagal membaca CLIENT_PAYLOAD: {e}")
    payload = {}

prompt = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')

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
    print("✅ Gambar adegan 1 berhasil disimpan.")
else:
    print(f"❌ Gagal mengunduh gambar AI (Status {img_response.status_code}). Exit.")
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

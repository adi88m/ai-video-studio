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
except Exception:
    payload = {}

prompt = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')

print("==========================================")
print(f"🚀 Memulai alur kerja render AI Video:")
print(f"   - Prompt Asli : {prompt}")
print(f"   - Voice       : {voice}")
print("==========================================")

# ---------------------------------------------------------
# 2. PENYESUAIAN & PEMBERSIHAN PROMPT (BAHASA INGGRIS)
# ---------------------------------------------------------
# Pemetaan kata kunci utama dari Bahasa Indonesia ke Inggris
prompt_map = {
    "candi kuno": "ancient ancient temple ruins, ancient stone temple",
    "tengah hutan": "deep dark forest",
    "misterius": "mysterious fog",
    "malam hari": "at night, glowing lights",
    "rumah tua": "old abandoned haunted house",
    "berkabut": "misty atmosphere",
    "planet bumi": "planet earth from space"
}

prompt_translated = prompt.lower()
for id_term, en_term in prompt_map.items():
    if id_term in prompt_translated:
        prompt_translated = prompt_translated.replace(id_term, en_term)

# Jika tidak ada di kamus, buat fallback prompt berbasis keyword umum
final_prompt_text = f"{prompt_translated}, {style} style, ultra realistic, highly detailed, 8k resolution, masterpiece"

# ---------------------------------------------------------
# 3. GENERATE GAMBAR VIA POLLINATIONS AI
# ---------------------------------------------------------
width, height = (720, 1280) if aspect == '9:16' else (1280, 720)
encoded_prompt = urllib.parse.quote(final_prompt_text)

# Menambahkan seed acak agar gambar selalu baru setiap kali di-render
random_seed = int(os.urandom(2).hex(), 16)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={random_seed}"

print(f"🎨 Encoded Prompt: {final_prompt_text}")
print(f"🌐 Mengunduh gambar AI: {image_url}")

try:
    img_response = requests.get(image_url, timeout=60)
    if img_response.status_code == 200:
        with open("scene1.jpg", "wb") as f:
            f.write(img_response.content)
        print("✅ Gambar adegan 1 berhasil disimpan.")
    else:
        print(f"❌ Gagal mengunduh gambar AI (Status {img_response.status_code}). Exit.")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error mengunduh gambar: {e}")
    sys.exit(1)

# ---------------------------------------------------------
# 4. GENERATE AUDIO SUARA AI (EDGE-TTS)
# ---------------------------------------------------------
audio_file = "audio1.mp3"
os.system(f'edge-tts --text "{narasi}" --voice "{voice}" --write-media {audio_file}')

if not os.path.exists(audio_file):
    print("❌ Gagal membuat audio TTS. Exit.")
    sys.exit(1)

# ---------------------------------------------------------
# 5. RENDER VIDEO MOVIEPY
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

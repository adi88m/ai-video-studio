import os
import sys
import json
import random
import requests
import urllib.parse
from PIL import Image
from moviepy.editor import (
    VideoClip, 
    AudioFileClip, 
    TextClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    CompositeAudioClip
)
from moviepy.audio.AudioClip import concatenate_audioclips

# ---------------------------------------------------------
# 1. PARSING INPUT DATA LENGKAP DARI WEB FRONTEND
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

# Main Parameters
prompt1 = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi1_a = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice_a = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')

# Extra Parameters Parsing
extra_raw = payload.get('extra', '{}')
try:
    extra_data = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
except Exception:
    extra_data = {}

voice_b = extra_data.get('voice_b1', '')
narasi1_b = extra_data.get('narasi_b1', '')
prompt2 = extra_data.get('prompt2', '')
narasi2 = extra_data.get('narasi2', '')
watermark_text = extra_data.get('watermark', '')

# Resolusi Canvas (W x H)
w, h = (720, 1280) if aspect == '9:16' else (1280, 720)

print("==========================================")
print(f"🚀 AI Video Engine Engine v3.0 Ultimate")
print(f"   - Canvas       : {w}x{h} ({aspect})")
print(f"   - Prompt 1     : {prompt1}")
print(f"   - Prompt 2     : {prompt2}")
print("==========================================")

# ---------------------------------------------------------
# 2. GENERATOR GAMBAR AI (WITH RANDOM SEED & TRANSLATION)
# ---------------------------------------------------------
def generate_ai_image(prompt_text, filename):
    prompt_map = {
        "candi kuno": "ancient stone temple ruins",
        "tengah hutan": "deep dark mystical forest",
        "malam hari": "at night with moonlight",
        "gerbang emas": "glowing golden ancient gate",
        "rumah tua": "old haunted abandoned mansion",
        "berkabut": "heavy mystical fog"
    }
    translated = prompt_text.lower()
    for id_term, en_term in prompt_map.items():
        translated = translated.replace(id_term, en_term)
        
    final_p = f"{translated}, {style} style, ultra-detailed 8k render, cinematic lighting"
    encoded = urllib.parse.quote(final_p)
    seed = random.randint(10000, 99999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={seed}"
    
    print(f"🎨 Generating Image: {url}")
    res = requests.get(url, timeout=60)
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        return True
    return False

# ---------------------------------------------------------
# 3. ANIMATION ENGINE: MEMBUAT VISUAL BERGERAK (PIL PAN/ZOOM)
# ---------------------------------------------------------
def make_motion_clip(img_path, duration, mode="zoom_in"):
    """Mengubah gambar statis menjadi animasi video bergerak per frame."""
    pil_img = Image.open(img_path).convert('RGB')
    orig_w, orig_h = pil_img.size

    def make_frame(t):
        progress = t / duration if duration > 0 else 0
        if mode == "zoom_in":
            scale = 1.0 + (0.15 * progress)  # Zoom in 100% -> 115%
        else:
            scale = 1.15 - (0.15 * progress)  # Zoom out 115% -> 100%

        crop_w = int(orig_w / scale)
        crop_h = int(orig_h / scale)
        left = (orig_w - crop_w) // 2
        top = (orig_h - crop_h) // 2

        cropped = pil_img.crop((left, top, left + crop_w, top + crop_h))
        resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
        return import_np_array(resized)

    def import_np_array(pil_image):
        import numpy as np
        return np.array(pil_image)

    return VideoClip(make_frame, duration=duration)

# ---------------------------------------------------------
# 4. PROSES ADEGAN 1 (AUDIO A + B DIALOG & VISUAL BERGERAK)
# ---------------------------------------------------------
print("🎬 Processing Scene 1...")
if not generate_ai_image(prompt1, "scene1.jpg"):
    sys.exit(1)

# Audio Karakter A
os.system(f'edge-tts --text "{narasi1_a}" --voice "{voice_a}" --write-media "audio1_a.mp3"')
audio_clips_1 = [AudioFileClip("audio1_a.mp3")]

# Audio Karakter B (Jika diisi)
if voice_b and narasi1_b:
    print("🗣️ Generating Voice Character B...")
    os.system(f'edge-tts --text "{narasi1_b}" --voice "{voice_b}" --write-media "audio1_b.mp3"')
    audio_clips_1.append(AudioFileClip("audio1_b.mp3"))

audio_scene_1 = concatenate_audioclips(audio_clips_1)
duration_1 = audio_scene_1.duration

# Buat Animasi Video Bergerak Adegan 1
video_scene_1 = make_motion_clip("scene1.jpg", duration_1, mode="zoom_in").set_audio(audio_scene_1)
all_scenes = [video_scene_1]

# ---------------------------------------------------------
# 5. PROSES ADEGAN 2 (JIKA DIISI DI APLIKASI WEB)
# ---------------------------------------------------------
if prompt2 and narasi2:
    print("🎬 Processing Scene 2...")
    if generate_ai_image(prompt2, "scene2.jpg"):
        os.system(f'edge-tts --text "{narasi2}" --voice "{voice_a}" --write-media "audio2.mp3"')
        audio_scene_2 = AudioFileClip("audio2.mp3")
        duration_2 = audio_scene_2.duration
        
        # Buat Animasi Video Bergerak Adegan 2 (Zoom Out)
        video_scene_2 = make_motion_clip("scene2.jpg", duration_2, mode="zoom_out").set_audio(audio_scene_2)
        all_scenes.append(video_scene_2)

# Gabungkan Semua Adegan Video
final_video = concatenate_videoclips(all_scenes, method="compose")
total_duration = final_video.duration

# ---------------------------------------------------------
# 6. RENDER KE MP4
# ---------------------------------------------------------
output_filename = "output_video.mp4"
print(f"📽️ Exporting Animation MP4 (Duration: {total_duration:.2f}s)...")

final_video.write_videofile(
    output_filename,
    fps=24,
    codec='libx264',
    audio_codec='aac',
    preset='ultrafast'
)

# Free Memory
final_video.close()
for sc in all_scenes: sc.close()

print("✅ Complete AI Motion Video Rendered Successfully!")

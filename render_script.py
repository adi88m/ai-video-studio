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
    CompositeVideoClip, 
    concatenate_videoclips, 
    CompositeAudioClip
)
from moviepy.audio.AudioClip import concatenate_audioclips

# ---------------------------------------------------------
# 1. PARSING INPUT DATA DARI GITHUB ACTIONS
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

prompt1 = payload.get('prompt', 'candi kuno di tengah hutan misterius malam hari')
narasi1_a = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice_a = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')

voice_b = payload.get('voice_b1', '')
narasi1_b = payload.get('narasi_b1', '')
prompt2 = payload.get('prompt2', '')
narasi2 = payload.get('narasi2', '')

w, h = (720, 1280) if aspect == '9:16' else (1280, 720)

print("==========================================")
print(f"🚀 AI Video Engine v3.0 Stable Active")
print(f"   - Style Visual : {style}")
print(f"   - Voice A      : {voice_a}")
print("==========================================")

# ---------------------------------------------------------
# 2. GENERATOR TTS AMAN (STABLE EDGE-TTS CALL)
# ---------------------------------------------------------
def generate_audio_tts(text, voice_name, style_visual, output_mp3):
    """Memanggil edge-tts secara langsung tanpa file XML yang memicu syntax error."""
    if not text.strip():
        return False

    # Pengaturan kecepatan dan nada berdasarkan mood/style visual
    rate_param = "-15%" if style_visual == "horror" else ("+10%" if style_visual in ["cyberpunk", "anime"] else "+0%")
    pitch_param = "-10Hz" if style_visual == "horror" else ("+5Hz" if style_visual in ["cyberpunk", "anime"] else "+0Hz")

    # Bersihkan kutipan dari teks agar tidak merusak perintah bash CLI
    clean_text = text.replace('"', '\\"').replace("'", "")

    cmd = f'edge-tts --text "{clean_text}" --voice "{voice_name}" --rate="{rate_param}" --pitch="{pitch_param}" --write-media "{output_mp3}"'
    print(f"🗣️ Running TTS Command: {cmd}")
    os.system(cmd)

    if not os.path.exists(output_mp3) or os.path.getsize(output_mp3) == 0:
        print(f"⚠️ Fallback TTS tanpa rate/pitch untuk {output_mp3}...")
        os.system(f'edge-tts --text "{clean_text}" --voice "{voice_name}" --write-media "{output_mp3}"')

    return os.path.exists(output_mp3)

# ---------------------------------------------------------
# 3. GENERATOR GAMBAR POLLINATIONS AI
# ---------------------------------------------------------
def generate_ai_image(prompt_text, filename):
    if not prompt_text.strip():
        return False
        
    prompt_map = {
        "candi kuno": "ancient stone temple ruins",
        "tengah hutan": "deep dark mystical forest",
        "malam hari": "at night with moonlight",
        "gerbang emas": "glowing golden ancient gate"
    }
    translated = prompt_text.lower()
    for id_term, en_term in prompt_map.items():
        translated = translated.replace(id_term, en_term)
        
    final_p = f"{translated}, {style} style, ultra-detailed 8k render, masterpiece, cinematic lighting"
    encoded = urllib.parse.quote(final_p)
    seed = random.randint(10000, 99999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={seed}"
    
    print(f"🎨 Generating Image ({filename}): {url}")
    try:
        res = requests.get(url, timeout=60)
        if res.status_code == 200:
            with open(filename, "wb") as f:
                f.write(res.content)
            return True
    except Exception as e:
        print(f"Error download image: {e}")
    return False

# ---------------------------------------------------------
# 4. ANIMATION ENGINE: EFEK KAMERA GERAK (PIL ZOOM)
# ---------------------------------------------------------
def make_motion_clip(img_path, duration, mode="zoom_in"):
    pil_img = Image.open(img_path).convert('RGB')
    orig_w, orig_h = pil_img.size

    def make_frame(t):
        progress = t / duration if duration > 0 else 0
        if mode == "zoom_in":
            scale = 1.0 + (0.15 * progress)
        else:
            scale = 1.15 - (0.15 * progress)

        crop_w = int(orig_w / scale)
        crop_h = int(orig_h / scale)
        left = (orig_w - crop_w) // 2
        top = (orig_h - crop_h) // 2

        cropped = pil_img.crop((left, top, left + crop_w, top + crop_h))
        resized = cropped.resize((w, h), Image.Resampling.LANCZOS)
        
        import numpy as np
        return np.array(resized)

    return VideoClip(make_frame, duration=duration)

# ---------------------------------------------------------
# 5. PROSES ADEGAN 1 (AUDIO A & B + VISUAL BERGERAK)
# ---------------------------------------------------------
print("🎬 Processing Scene 1...")
if not generate_ai_image(prompt1, "scene1.jpg"):
    print("❌ Gagal membuat gambar adegan 1.")
    sys.exit(1)

# Generate Audio TTS Karakter A
if not generate_audio_tts(narasi1_a, voice_a, style, "audio1_a.mp3"):
    print("❌ Gagal membuat audio Karakter A.")
    sys.exit(1)

audio_clips_1 = [AudioFileClip("audio1_a.mp3")]

# Generate Audio TTS Karakter B (Jika diisi)
if voice_b and narasi1_b.strip():
    print("🗣️ Generating Dialog Character B...")
    if generate_audio_tts(narasi1_b, voice_b, style, "audio1_b.mp3"):
        audio_clips_1.append(AudioFileClip("audio1_b.mp3"))

audio_scene_1 = concatenate_audioclips(audio_clips_1)
duration_1 = audio_scene_1.duration

video_scene_1 = make_motion_clip("scene1.jpg", duration_1, mode="zoom_in").set_audio(audio_scene_1)
all_scenes = [video_scene_1]

# ---------------------------------------------------------
# 6. PROSES ADEGAN 2 (JIKA DIISI)
# ---------------------------------------------------------
if prompt2.strip() and narasi2.strip():
    print("🎬 Processing Scene 2...")
    if generate_ai_image(prompt2, "scene2.jpg") and generate_audio_tts(narasi2, voice_a, style, "audio2.mp3"):
        audio_scene_2 = AudioFileClip("audio2.mp3")
        duration_2 = audio_scene_2.duration
        video_scene_2 = make_motion_clip("scene2.jpg", duration_2, mode="zoom_out").set_audio(audio_scene_2)
        all_scenes.append(video_scene_2)

# ---------------------------------------------------------
# 7. EXPORT FINAL MP4
# ---------------------------------------------------------
final_video = concatenate_videoclips(all_scenes, method="compose")
total_duration = final_video.duration

output_filename = "output_video.mp4"
print(f"📽️ Exporting MP4 (Duration: {total_duration:.2f}s)...")

final_video.write_videofile(
    output_filename,
    fps=24,
    codec='libx264',
    audio_codec='aac',
    preset='ultrafast'
)

final_video.close()
for sc in all_scenes: sc.close()

print("✅ Render MP4 Berhasil Dituntaskan!")

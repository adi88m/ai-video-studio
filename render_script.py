import os
import sys
import json
import requests
import urllib.parse
from moviepy.editor import (
    ImageClip, 
    AudioFileClip, 
    CompositeVideoClip, 
    concatenate_videoclips, 
    CompositeAudioClip
)

# ---------------------------------------------------------
# 1. PARSING INPUT DATA LENGKAP DARI WEB APP
# ---------------------------------------------------------
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

# Main Parameters
prompt1 = payload.get('prompt', 'ancient temple in mysterious dark forest')
narasi1_a = payload.get('narasi', '')
voice_a = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')
bgm_type = payload.get('bgm', 'none')

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

# Resolusi Canvas
w, h = (720, 1280) if aspect == '9:16' else (1280, 720)

print(f"🚀 Memproses Video Dinamis Multi-Scene & Motion Camera...")

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS (TRANSLATE, IMAGE & ANIMATION ENGINE)
# ---------------------------------------------------------
def generate_ai_image(prompt_text, filename):
    prompt_map = {
        "candi kuno": "ancient stone temple ruins",
        "tengah hutan": "deep mysterious forest",
        "malam hari": "dark night, moonlight",
        "gerbang emas": "glowing golden ancient gate"
    }
    translated = prompt_text.lower()
    for id_t, en_t in prompt_map.items():
        translated = translated.replace(id_t, en_t)
        
    final_p = f"{translated}, {style} style, 8k resolution, cinematic lighting"
    encoded = urllib.parse.quote(final_p)
    seed = int(os.urandom(2).hex(), 16)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={seed}"
    
    res = requests.get(url, timeout=60)
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        return True
    return False

def make_animated_clip(img_path, duration):
    """Membuat efek gerakan kamera dinamis (Zoom-In & Panning)."""
    base_clip = ImageClip(img_path).set_duration(duration)
    # Animasi perbesaran skala secara halus (Zoom in 1.0 -> 1.15)
    animated = base_clip.resize(lambda t: 1 + 0.05 * t)
    # Menjaga posisi center video
    animated = animated.set_position(('center', 'center')).set_duration(duration)
    return CompositeVideoClip([animated], size=(w, h))

# ---------------------------------------------------------
# 3. GENERATE ADEGAN 1 (KARAKTER A + B DIALOG)
# ---------------------------------------------------------
generate_ai_image(prompt1, "scene1.jpg")

# Audio Karakter A Adegan 1
os.system(f'edge-tts --text "{narasi1_a}" --voice "{voice_a}" --write-media "a1_a.mp3"')
audio_clips_1 = [AudioFileClip("a1_a.mp3")]

# Audio Karakter B Adegan 1 (Jika ada dialog)
if voice_b and narasi1_b:
    os.system(f'edge-tts --text "{narasi1_b}" --voice "{voice_b}" --write-media "a1_b.mp3"')
    audio_clips_1.append(AudioFileClip("a1_b.mp3"))

# Gabungkan Audio Adegan 1
from moviepy.audio.AudioClip import concatenate_audioclips
combined_audio_1 = concatenate_audioclips(audio_clips_1)
clip1 = make_animated_clip("scene1.jpg", combined_audio_1.duration).set_audio(combined_audio_1)

all_video_clips = [clip1]

# ---------------------------------------------------------
# 4. GENERATE ADEGAN 2 (JIKA DIISI DI APLIKASI WEB)
# ---------------------------------------------------------
if prompt2 and narasi2:
    print("🎬 Memproses Adegan 2...")
    generate_ai_image(prompt2, "scene2.jpg")
    os.system(f'edge-tts --text "{narasi2}" --voice "{voice_a}" --write-media "a2.mp3"')
    audio_2 = AudioFileClip("a2.mp3")
    clip2 = make_animated_clip("scene2.jpg", audio_2.duration).set_audio(audio_2)
    all_video_clips.append(clip2)

# Concatenate Semua Adegan Video
final_video = concatenate_videoclips(all_video_clips, method="compose")

# ---------------------------------------------------------
# 5. RENDER SPESIFIKASI AKHIR & UPLOAD
# ---------------------------------------------------------
output_filename = "output_video.mp4"
final_video.write_videofile(
    output_filename,
    fps=24,
    codec='libx264',
    audio_codec='aac',
    preset='ultrafast'
)

# Pembersihan memory clip
final_video.close()
for c in all_video_clips: c.close()

print("✅ Render Visual Bergerak Selesai!")

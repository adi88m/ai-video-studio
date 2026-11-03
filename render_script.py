import os
import sys
import json
import random
import requests
import urllib.parse
import numpy as np

from moviepy.editor import (
    ImageClip, 
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
prompt1 = payload.get('prompt', 'ancient stone temple in dark mysterious forest at night')
narasi1_a = payload.get('narasi', 'Dia berjalan menyusuri tempat suci yang telah lama terlupakan.')
voice_a = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')
bgm_choice = payload.get('bgm', 'none')

# Extra Parameters Parsing (JSON String)
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

# Resolusi Canvas
w, h = (720, 1280) if aspect == '9:16' else (1280, 720)

print("==========================================")
print(f"🚀 AI Video Engine v3.0 Ultimate Started")
print(f"   - Canvas       : {w}x{h} ({aspect})")
print(f"   - Style Visual : {style}")
print(f"   - BGM          : {bgm_choice}")
print("==========================================")

# ---------------------------------------------------------
# 2. HELPER: PENERJEMAH PROMPT & GENERATOR GAMBAR AI
# ---------------------------------------------------------
def generate_ai_image(prompt_text, filename):
    prompt_map = {
        "candi kuno": "ancient stone temple ruins",
        "tengah hutan": "deep mysterious forest",
        "malam hari": "dark night, moonlight",
        "gerbang emas": "glowing golden ancient gate",
        "rumah tua": "old haunted abandoned mansion",
        "berkabut": "heavy mystical fog"
    }
    translated = prompt_text.lower()
    for id_term, en_term in prompt_map.items():
        translated = translated.replace(id_term, en_term)
        
    final_p = f"{translated}, {style} style, ultra-detailed 8k render, masterpiece, dramatic atmospheric lighting"
    encoded = urllib.parse.quote(final_p)
    seed = random.randint(1000, 99999)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&seed={seed}"
    
    print(f"🎨 Generating Image via Pollinations AI...")
    res = requests.get(url, timeout=60)
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        return True
    return False

# ---------------------------------------------------------
# 3. HELPER: MEMBUAT VISUAL BERGERAK (EFEK CAMERA MOTION 3D)
# ---------------------------------------------------------
def make_3d_motion_clip(img_path, duration, motion_type="zoom_in"):
    """Mengubah gambar statis menjadi visual video bergerak (Panning/Zoom 3D)."""
    base_clip = ImageClip(img_path).set_duration(duration)
    
    if motion_type == "zoom_in":
        # Efek perbesaran sinematik perlahan (Zoom-In 1.0 -> 1.12)
        animated = base_clip.resize(lambda t: 1.0 + (0.12 * (t / duration)))
    else:
        # Efek perkecilan (Zoom-Out 1.12 -> 1.0)
        animated = base_clip.resize(lambda t: 1.12 - (0.12 * (t / duration)))
        
    return CompositeVideoClip([animated.set_position(('center', 'center'))], size=(w, h)).set_duration(duration)

# ---------------------------------------------------------
# 4. HELPER: SYNTHETIC BGM (MUSIK LATAR) GENERATOR
# ---------------------------------------------------------
def generate_background_music(duration, bg_type):
    """Membuat synth audio background otomatis sesuai tipe suasana BGM."""
    if bg_type == "none" or duration <= 0:
        return None
    
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    if bg_type == "horror":
        # Frekuensi rendah mengalun misterius
        freq = 55  # Note A1
        wave = 0.1 * np.sin(2 * np.pi * freq * t) + 0.05 * np.sin(2 * np.pi * (freq + 3) * t)
    elif bg_type == "epic":
        # Vibrasi frekuensi dramatic
        freq = 110
        wave = 0.1 * np.sin(2 * np.pi * freq * t) + 0.08 * np.sin(2 * np.pi * (freq * 1.5) * t)
    else:  # ambient
        # Ambient cinematic lembut
        freq = 220
        wave = 0.08 * np.sin(2 * np.pi * freq * t)
        
    # Formatting audio numpy ke file WAV sementara
    from scipy.io.wavfile import write
    audio_int16 = (wave * 32767).astype(np.int16)
    write("temp_bgm.wav", sample_rate, audio_int16)
    
    return AudioFileClip("temp_bgm.wav").set_duration(duration)

# ---------------------------------------------------------
# 5. GENERATE ADEGAN 1 (AUDIO DIALOG A & B + VISUAL BERGERAK)
# ---------------------------------------------------------
print("🎬 Processing Scene 1...")
if not generate_ai_image(prompt1, "scene1.jpg"):
    sys.exit(1)

# Generate Audio Karakter A
os.system(f'edge-tts --text "{narasi1_a}" --voice "{voice_a}" --write-media "audio1_a.mp3"')
audio_clips_1 = [AudioFileClip("audio1_a.mp3")]

# Generate Audio Karakter B (Jika diisi)
if voice_b and narasi1_b:
    os.system(f'edge-tts --text "{narasi1_b}" --voice "{voice_b}" --write-media "audio1_b.mp3"')
    audio_clips_1.append(AudioFileClip("audio1_b.mp3"))

# Gabungkan Audio Dialog Adegan 1
audio_scene_1 = concatenate_audioclips(audio_clips_1)
duration_1 = audio_scene_1.duration

# Buat Visual Video Bergerak untuk Adegan 1
video_scene_1 = make_3d_motion_clip("scene1.jpg", duration_1, motion_type="zoom_in").set_audio(audio_scene_1)
all_scenes = [video_scene_1]

# ---------------------------------------------------------
# 6. GENERATE ADEGAN 2 (JIKA DIISI DI APLIKASI WEB)
# ---------------------------------------------------------
if prompt2 and narasi2:
    print("🎬 Processing Scene 2...")
    if generate_ai_image(prompt2, "scene2.jpg"):
        os.system(f'edge-tts --text "{narasi2}" --voice "{voice_a}" --write-media "audio2.mp3"')
        audio_scene_2 = AudioFileClip("audio2.mp3")
        duration_2 = audio_scene_2.duration
        
        # Buat Visual Video Bergerak untuk Adegan 2 (Zoom Out)
        video_scene_2 = make_3d_motion_clip("scene2.jpg", duration_2, motion_type="zoom_out").set_audio(audio_scene_2)
        all_scenes.append(video_scene_2)

# Concatenate Multi-Adegan Video
main_video = concatenate_videoclips(all_scenes, method="compose")
total_duration = main_video.duration

# ---------------------------------------------------------
# 7. PENGGABUNGAN BGM & WATERMARK EFEK
# ---------------------------------------------------------
# Penambahan Musik Latar BGM
bgm_clip = generate_background_music(total_duration, bgm_choice)
if bgm_clip:
    final_audio = CompositeAudioClip([main_video.audio, bgm_clip.volumex(0.3)])
    main_video = main_video.set_audio(final_audio)

final_overlays = [main_video]

# Penambahan Watermark Username (Jika diisi)
if watermark_text:
    try:
        txt_clip = (TextClip(watermark_text, fontsize=24, color='white', font='Arial')
                    .set_position(('right', 'bottom'))
                    .set_duration(total_duration)
                    .margin(right=20, bottom=20, opacity=0))
        final_overlays.append(txt_clip)
    except Exception as e:
        print(f"⚠️ Skip watermark text clip: {e}")

final_output_video = CompositeVideoClip(final_overlays, size=(w, h)).set_duration(total_duration)

# ---------------------------------------------------------
# 8. RENDER SPESIFIKASI FINAL MP4 & PEMBERSIHAN
# ---------------------------------------------------------
output_filename = "output_video.mp4"
print(f"📽️ Exporting Complete Dynamic Video (Total Duration: {total_duration:.2f}s)...")

final_output_video.write_videofile(
    output_filename,
    fps=24,
    codec='libx264',
    audio_codec='aac',
    preset='ultrafast'
)

# Close & release resources
final_output_video.close()
main_video.close()
for sc in all_scenes: sc.close()

print("✅ Complete AI Video Rendering Finished Successfully!")

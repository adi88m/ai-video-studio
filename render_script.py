import os
import sys
import asyncio
import urllib.parse
import requests
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips, composite_audioclips

async def make_voiceover(text, voice_code, output_file):
    communicate = edge_tts.Communicate(text, voice_code)
    await communicate.save(output_file)

def apply_lip_sync(image_path, audio_path, output_video):
    """Integrasi SadTalker / Wav2Lip untuk Animasi Wajah & Mulut"""
    try:
        print("  [Lip-Sync] Memproses gerakan bibir karakter dengan AI...")
        # Memanggil pustaka/script SadTalker lokal jika tersedia
        cmd = f"python SadTalker/inference.py --driven_audio {audio_path} --source_image {image_path} --result_dir ./sadtalker_out --still --preprocess full"
        os.system(cmd)
        
        # Lokasi video hasil lip-sync SadTalker
        generated_mp4 = "./sadtalker_out/result.mp4"
        if os.path.exists(generated_mp4):
            return generated_mp4
    except Exception as e:
        print(f"  [Warning] Lip-Sync fallback ke statis: {e}")
    return None

def generate_scene(prompt, narasi, voice_code, aspect_ratio, motion_effect, style_preset, sub_color, sub_bg, enable_lipsync, res_w, res_h, scene_idx, voice_b="", narasi_b=""):
    w, h = res_w, res_h

    styled_prompt = prompt
    if style_preset == "cinematic":
        styled_prompt += ", highly detailed, 8k resolution, cinematic lighting, photorealistic"
    elif style_preset == "anime":
        styled_prompt += ", vibrant anime style, makoto shinkai aesthetic, detailed digital art"
    elif style_preset == "cyberpunk":
        styled_prompt += ", cyberpunk style, neon lights, futuristic city aesthetic"
    elif style_preset == "horror":
        styled_prompt += ", dark creepy atmosphere, horror aesthetic, eerie lighting"

    print(f"[{scene_idx}] Mengunduh gambar AI ({style_preset}): {styled_prompt}")
    encoded_prompt = urllib.parse.quote(styled_prompt)
    img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&nologo=true"
    
    img_file = f"bg_{scene_idx}.jpg"
    audio_a_file = f"voice_a_{scene_idx}.mp3"
    audio_b_file = f"voice_b_{scene_idx}.mp3"
    
    try:
        res = requests.get(img_url, timeout=30)
        res.raise_for_status()
        with open(img_file, "wb") as f:
            f.write(res.content)
    except Exception as e:
        print(f"Error gambar scene {scene_idx}: {e}")
        sys.exit(1)

    # 1. Generate Voiceover A
    asyncio.run(make_voiceover(narasi, voice_code, audio_a_file))
    audio_clip_a = AudioFileClip(audio_a_file)

    # 2. Cek Dialog Karakter B (Jika diisi)
    if narasi_b.strip() and voice_b.strip():
        asyncio.run(make_voiceover(narasi_b, voice_b, audio_b_file))
        audio_clip_b = AudioFileClip(audio_b_file)
        combined_voice = composite_audioclips([audio_clip_a, audio_clip_b.set_start(audio_clip_a.duration)])
        total_duration = audio_clip_a.duration + audio_clip_b.duration
    else:
        combined_voice = audio_clip_a
        total_duration = audio_clip_a.duration

    # Cek Animasi Lip-Sync
    lipsync_video = None
    if enable_lipsync == "true":
        lipsync_video = apply_lip_sync(img_file, audio_a_file, f"lipsync_{scene_idx}.mp4")

    if lipsync_video and os.path.exists(lipsync_video):
        img_clip = VideoFileClip(lipsync_video).set_duration(total_duration).resize((w, h))
    else:
        img_clip = ImageClip(img_file).set_duration(total_duration).resize((w, h))

        # Smart Camera Movement (Pan / Tilt / Zoom)
        if motion_effect == "zoom_in":
            img_clip = img_clip.resize(lambda t: 1 + 0.04 * t)
        elif motion_effect == "zoom_out":
            img_clip = img_clip.resize(lambda t: 1.2 - 0.04 * t)
        elif motion_effect == "pan_left":
            img_clip = img_clip.set_position(lambda t: (int(-20 * t), 'center'))

    img_clip = img_clip.set_audio(combined_voice)

    # Subtitle Overlay
    try:
        display_text = f"{narasi}\n{narasi_b}".strip()
        txt_clip = TextClip(
            display_text, 
            fontsize=32 if aspect_ratio == "9:16" else 26, 
            color=sub_color, 
            bg_color=sub_bg if sub_bg != "transparent" else None,
            size=(w - 80, None), 
            method='caption'
        ).set_duration(total_duration).set_position(('center', h - 180))

        final_scene = CompositeVideoClip([img_clip, txt_clip])
    except Exception as e:
        print(f"Warning Subtitle: {e}")
        final_scene = img_clip

    return final_scene

def generate_video():
    prompt1 = os.environ.get("PROMPT", "candi kuno di tengah hutan")
    narasi1 = os.environ.get("NARASI", "Dia berjalan menyusuri tempat suci.")
    voice_b1 = os.environ.get("VOICE_B1", "")
    narasi_b1 = os.environ.get("NARASI_B1", "")

    prompt2 = os.environ.get("PROMPT2", "")
    narasi2 = os.environ.get("NARASI2", "")
    
    voice_code = os.environ.get("VOICE", "id-ID-ArdiNeural")
    aspect_ratio = os.environ.get("ASPECT", "9:16")
    motion_effect = os.environ.get("MOTION", "zoom_in")
    style_preset = os.environ.get("STYLE", "cinematic")
    bgm_option = os.environ.get("BGM", "none")
    sub_color = os.environ.get("SUB_COLOR", "yellow")
    sub_bg = os.environ.get("SUB_BG", "black")
    enable_lipsync = os.environ.get("LIPSYNC", "false")
    resolution = os.environ.get("RESOLUTION", "720p")
    watermark_text = os.environ.get("WATERMARK", "")

    # Tentukan Resolusi
    if aspect_ratio == "16:9":
        res_w, res_h = (1920, 1080) if resolution == "1080p" else (1280, 720)
    else:
        res_w, res_h = (1080, 1920) if resolution == "1080p" else (720, 1280)

    scenes = []
    scenes.append(generate_scene(prompt1, narasi1, voice_code, aspect_ratio, motion_effect, style_preset, sub_color, sub_bg, enable_lipsync, res_w, res_h, 1, voice_b1, narasi_b1))

    if prompt2.strip() and narasi2.strip():
        scenes.append(generate_scene(prompt2, narasi2, voice_code, aspect_ratio, motion_effect, style_preset, sub_color, sub_bg, enable_lipsync, res_w, res_h, 2))

    print("[+] Merender gabungan adegan...")
    final_video = concatenate_videoclips(scenes, method="compose")

    # Watermark Overlay
    if watermark_text.strip():
        try:
            wm_clip = TextClip(watermark_text, fontsize=20, color='white', opacity=0.6).set_duration(final_video.duration).set_position(('right', 'top'))
            final_video = CompositeVideoClip([final_video, wm_clip])
        except Exception as e:
            print(f"Warning Watermark: {e}")

    # BGM Integrasi
    if bgm_option != "none":
        bgm_url_map = {
            "ambient": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
            "epic": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3",
            "horror": "https://cdn.pixabay.com/download/audio/2022/10/14/audio_9930a6df31.mp3"
        }
        if bgm_option in bgm_url_map:
            try:
                bgm_res = requests.get(bgm_url_map[bgm_option], timeout=30)
                with open("bgm.mp3", "wb") as bf:
                    bf.write(bgm_res.content)
                bgm_clip = AudioFileClip("bgm.mp3").volumex(0.12).set_duration(final_video.duration)
                combined_audio = composite_audioclips([final_video.audio, bgm_clip])
                final_video = final_video.set_audio(combined_audio)
            except Exception as e:
                print(f"Warning BGM: {e}")

    output_path = "output.mp4"
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2
    )

    print("[+] Mengunggah ke Cloud Storage (Catbox)...")
    try:
        with open(output_path, "rb") as f:
            upload_res = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                timeout=60
            )
        video_url = upload_res.text.strip()
        print(f"CATBOX_URL_RESULT:{video_url}")
    except Exception as e:
        print(f"Error upload: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_video()

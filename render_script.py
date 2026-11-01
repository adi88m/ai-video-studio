import os
import sys
import urllib.parse
import requests
from gTTS import gTTS
from moviepy.editor import ImageClip, AudioFileClip

def generate_video():
    prompt = os.environ.get("PROMPT", "cinematic photo of ancient temple in mystery forest")
    narasi = os.environ.get("NARASI", "Dia berjalan menyusuri tempat suci yang telah lama terlupakan.")

    print(f"[1/4] Mengunduh gambar AI untuk prompt: {prompt}")
    encoded_prompt = urllib.parse.quote(f"cinematic photo of {prompt}")
    img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"
    
    try:
        response = requests.get(img_url, timeout=30)
        response.raise_for_status()
        with open("bg.jpg", "wb") as f:
            f.write(response.content)
        print("  -> Gambar berhasil diunduh.")
    except Exception as e:
        print(f"  -> Error unduh gambar: {e}")
        sys.exit(1)

    print(f"[2/4] Membuat voiceover Bahasa Indonesia untuk narasi: {narasi}")
    try:
        tts = gTTS(text=narasi, lang='id')
        tts.save("voice.mp3")
        print("  -> Audio voiceover berhasil dibuat.")
    except Exception as e:
        print(f"  -> Error gTTS: {e}")
        sys.exit(1)

    print("[3/4] Merender video .MP4 dengan efek Ken Burns Zoom & FFmpeg...")
    try:
        audio_clip = AudioFileClip("voice.mp3")
        duration = audio_clip.duration

        img_clip = ImageClip("bg.jpg").set_duration(duration).resize((720, 1280))
        img_clip = img_clip.resize(lambda t: 1 + 0.05 * t)  # Efek Zoom Gerak Perlahan
        img_clip = img_clip.set_audio(audio_clip)

        output_path = "output.mp4"
        img_clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=2
        )
        print(f"[4/4] Video berhasil dirender: {output_path}")
    except Exception as e:
        print(f"  -> Error rendering video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_video()

import os
import sys
import asyncio
import urllib.parse
import requests
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

async def make_voiceover(text, output_file):
    # Menggunakan suara AI Bahasa Indonesia (id-ID-ArdiNeural)
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

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

    print(f"[2/4] Membuat voiceover Bahasa Indonesia (Edge-TTS)...")
    try:
        asyncio.run(make_voiceover(narasi, "voice.mp3"))
        print("  -> File voice.mp3 berhasil dibuat.")
    except Exception as e:
        print(f"  -> Error TTS: {e}")
        sys.exit(1)

    print("[3/4] Merender video .MP4...")
    try:
        audio_clip = AudioFileClip("voice.mp3")
        duration = audio_clip.duration

        img_clip = ImageClip("bg.jpg").set_duration(duration)
        img_clip = img_clip.resize((720, 1280))
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
        
        audio_clip.close()
        img_clip.close()
        print(f"[4/4] Video berhasil dirender: {output_path}")
    except Exception as e:
        print(f"  -> Error rendering video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_video()

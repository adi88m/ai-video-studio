import os
import sys
import asyncio
import urllib.parse
import requests
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

async def make_voiceover(text, output_file):
    communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
    await communicate.save(output_file)

def generate_video():
    prompt = os.environ.get("PROMPT", "cinematic photo of ancient temple")
    narasi = os.environ.get("NARASI", "Dia berjalan menyusuri tempat suci.")

    # 1. Unduh Gambar
    encoded_prompt = urllib.parse.quote(f"cinematic photo of {prompt}")
    img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"
    img_bytes = requests.get(img_url, timeout=30).content
    with open("bg.jpg", "wb") as f:
        f.write(img_bytes)

    # 2. Buat Audio
    asyncio.run(make_voiceover(narasi, "voice.mp3"))

    # 3. Render Video MP4
    audio_clip = AudioFileClip("voice.mp3")
    duration = audio_clip.duration
    img_clip = ImageClip("bg.jpg").set_duration(duration).resize((720, 1280)).set_audio(audio_clip)
    img_clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=2)
    audio_clip.close()
    img_clip.close()

    # 4. Upload Otomatis ke Catbox agar bisa diputar langsung di Blogger
    print("[4/4] Mengunggah video ke cloud storage...")
    with open("output.mp4", "rb") as f:
        response = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f}
        )
    video_direct_url = response.text.strip()
    print(f"URL_VIDEO_FINAL:{video_direct_url}")

if __name__ == "__main__":
    generate_video()

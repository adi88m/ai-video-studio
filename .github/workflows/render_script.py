import os
import requests
import urllib.parse
from gTTS import gTTS
from moviepy.editor import ImageClip, AudioFileClip

prompt = os.environ.get("PROMPT", "cinematic landscape")
narasi = os.environ.get("NARASI", "Selamat datang di AI Video Studio.")

# 1. Unduh Gambar AI dari Pollinations
encoded_prompt = urllib.parse.quote(f"cinematic photo of {prompt}")
img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=720&height=1280&nologo=true"
img_bytes = requests.get(img_url).content
with open("bg.jpg", "wb") as f:
    f.write(img_bytes)

# 2. Buat Voiceover Bahasa Indonesia via gTTS
tts = gTTS(text=narasi, lang='id')
tts.save("voice.mp3")

# 3. Render Video MP4 (Ken Burns Zoom + Audio)
audio_clip = AudioFileClip("voice.mp3")
duration = audio_clip.duration

img_clip = ImageClip("bg.jpg").set_duration(duration).resize((720, 1280))
img_clip = img_clip.resize(lambda t: 1 + 0.05 * t)  # Animasi zoom gerak
img_clip = img_clip.set_audio(audio_clip)

img_clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")

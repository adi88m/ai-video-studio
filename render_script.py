import os
import sys
import json

# Mengambil payload dari environment variable GitHub Actions
payload_raw = os.environ.get('CLIENT_PAYLOAD', '{}')
try:
    payload = json.loads(payload_raw)
except Exception:
    payload = {}

# Parsing data utama
prompt = payload.get('prompt', '')
narasi = payload.get('narasi', '')
voice = payload.get('voice', 'id-ID-ArdiNeural')
aspect = payload.get('aspect', '9:16')
style = payload.get('style', 'cinematic')
bgm = payload.get('bgm', 'none')
lipsync = str(payload.get('lipsync', 'false')).lower() == 'true'

# Parsing data tambahan dari field 'extra'
extra_raw = payload.get('extra', '{}')
try:
    extra_data = json.loads(extra_raw) if isinstance(extra_raw, str) else extra_raw
except Exception:
    extra_data = {}

voice_b1 = extra_data.get('voice_b1', '')
narasi_b1 = extra_data.get('narasi_b1', '')
prompt2 = extra_data.get('prompt2', '')
narasi2 = extra_data.get('narasi2', '')
motion = extra_data.get('motion', 'zoom_in')
resolution = extra_data.get('resolution', '720p')
watermark = extra_data.get('watermark', '')

print(f"--> Memulai Render: Prompt='{prompt}', Voice='{voice}', Aspect='{aspect}'")

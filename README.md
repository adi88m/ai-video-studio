# 🎬 AI Video Studio Pro v3.0 Ultimate

[![GitHub Actions Status](https://img.shields.io/badge/Backend-GitHub%20Actions-blue?logo=githubactions)](https://github.com/adi88m/ai-video-studio/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-GitHub%20Pages%20%7C%20Blogger-orange)](#-penerapan-deployment)

**AI Video Studio Pro** adalah platform pembuatan video AI otomatis (*Single-Page Web Application*) yang mengintegrasikan pengolah gambar AI, sintesis suara multi-bahasa, rendering subtitle, serta animasi pergerakan visual secara langsung via cloud tanpa membutuhkan server fisik mandiri.

---

## 🌟 Fitur Utama (v3.0 Ultimate)

- **🎨 Multi-Style Visual Generator:** Mendukung berbagai *Style Preset* visual (Cinematic 3D, Anime/Manga, Cyberpunk, & Horror Dark) menggunakan **Pollinations AI**.
- **🗣️ Multi-Language Voiceover & Dialog 2 Orang:** Menggunakan **Edge-TTS** dengan pilihan suara beragam (Bahasa Indonesia, Jawa, Sunda, Inggris, Jepang, Korea) serta dukungan dialog interaktif antar dua karakter dalam 1 adegan.
- **👄 Lip-Sync Animation (SadTalker Integration):** Opsi animasi pergerakan bibir dan ekspresi wajah AI mengikuti ucapan voiceover.
- **📐 Aspek Rasio & Resolusi Kustom:** Format *Vertical (9:16)* untuk TikTok/Reels/Shorts dan *Horizontal (16:9)* untuk YouTube, dengan pilihan output **720p HD** atau **1080p Full HD**.
- **🎵 Background Music (BGM) & Subtitle Styling:** Penggabungan audio musik latar bebas hak cipta dengan pengatur *ducking* audio, serta subtitle otomatis dengan visualisasi warna kustom.
- **💡 One-Touch Story Templates:** Templat prompt cerita siap pakai (Horor, Edukasi, & Dialog) untuk mempercepat pembuatan video.
- **☁️ Cloud Direct Storage:** Hasil render video `.mp4` diunggah otomatis ke **Catbox.moe** untuk kemudahan pemutaran (*streaming*) dan unduhan instan.

---

## 🏗️ Arsitektur Sistem

```text
[ Browser / Frontend ] 
       │
       │ (1) Dispatch Event & Payload JSON
       ▼
[ GitHub Actions Runner (ubuntu-latest) ]
       │
       ├─ (2) Generate Image (Pollinations AI)
       ├─ (3) Generate Audio TTS (Edge-TTS)
       ├─ (4) Lip-Sync & Motion FX (SadTalker / FFmpeg / MoviePy)
       └─ (5) Render Final Video (.mp4)
       │
       │ (6) Upload Output
       ▼
[ Catbox.moe Cloud Storage ] ──> (7) Direct URL Video ke Web UI

# Kebijakan Keamanan (Security Policy) - AI Video Studio

Dokumen ini menjelaskan kebijakan keamanan, pengelolaan token, serta prosedur pelaporan kerentanan untuk proyek **AI Video Studio Pro**.

---

## 🔒 Kebijakan Keamanan Utamanya

Aplikasi ini beroperasi menggunakan arsitektur *Client-Serverless* (Frontend berbasis browser di GitHub Pages / Blogger dan Backend berbasis GitHub Actions Runner). 

### 1. Pengelolaan Personal Access Token (PAT)
* **Fine-Grained Token:** Pengguna WAJIB menggunakan **Fine-Grained Personal Access Token** yang dibatasi izinnya *hanya* untuk repositori backend ini.
* **Minimal Scope / Permissions:**
  * `Actions`: **Read and Write** (Diperlukan untuk memicu `repository_dispatch` dan mengambil log eksekusi).
  * `Contents`: **Read-only**.
  * `Metadata`: **Read-only** (Otomatis dari GitHub).
* **Proteksi Akun:** Jangan pernah menggunakan *Classic PAT* dengan cakupan `repo` (Full Control) pada kode frontend publik (`index.html`) untuk mencegah penyalahgunaan kuota render oleh pihak luar.

### 2. Privasi Data & File Video
* **Isolasi Lingkungan Render:** Seluruh eksekusi script Python (`render_script.py`) berjalan di dalam virtual container *ephemeral* GitHub Actions (`ubuntu-latest`). Semua file sementara (gambar `.jpg` dan audio `.mp3`) langsung dihapus otomatis saat runner selesai bekerja.
* **Penyimpanan Video (Catbox.moe):** Video hasil render diunggah ke *Catbox.moe* menggunakan *random string URL*. File tersebut tidak terindeks publik oleh mesin pencari dan hanya bisa diakses via tautan langsung.

---

## 🛡️ Versi yang Didukung (Supported Versions)

Kami memberikan pembaruan patch keamanan pada versi proyek berikut:

| Versi Proyek | Didukung Keamanannya | Catatan |
| :--- | :--- | :--- |
| `v3.0.x` (Ultimate) | 🟢 **Ya** | Versi aktif utama (Multi-Scene, Lip-Sync & BGM) |
| `v2.0.x` (Pro) | 🟡 **Terbatas** | Disarankan *upgrade* ke v3.0 |
| `< v2.0` | 🔴 **Tidak** | Versi usang, gunakan v3.0 |

---

## 🚨 Pelaporan Kerentanan Keamanan (Reporting a Vulnerability)

Jika Anda menemukan celah keamanan, kelemahan sistem, atau potensi kebocoran akses pada repositori ini:

1. **JANGAN** membuat isu terbuka (*Public Issue*) di repositori ini.
2. Laporkan temuan Anda secara privat melalui salah satu jalur berikut:
   * **Email:** [Alamat Email Anda / adi88m@gmail.com]
   * **GitHub Private Vulnerability Reporting:** Gunakan tombol **"Report a vulnerability"** di tab *Security* repositori ini jika aktif.

### Format Laporan:
* Deskripsi rinci mengenai celah keamanan yang ditemukan.
* Langkah-langkah untuk mereproduksi masalah (*Proof of Concept*).
* Potensi dampak keamanan terhadap repositori atau token pengguna.

Kami berkomitmen untuk meninjau dan merespons setiap laporan keamanan dalam waktu **24–48 jam**, serta merilis perbaikan secepat mungkin.

---

## 📜 Lisensi & Tanggung Jawab Pengguna
Proyek ini disediakan secara *As-Is* (apa adanya). Pengembang tidak bertanggung jawab atas habisnya kuota menit rendering GitHub Actions akibat penggunaan token publik tanpa pembatasan izin (*scope limitation*). Pengguna bertanggung jawab penuh atas keamanan token masing-masing.

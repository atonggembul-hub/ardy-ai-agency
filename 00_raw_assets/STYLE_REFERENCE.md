# Template Gaya Standar `editvidio` — Ardy AI Agency HQ

Dokumen ini adalah acuan gaya visual resmi untuk **Jubaidah** (`jubaidah-editor` + `editvidio`), disarikan dari 4 video referensi di Google Drive `00_raw_assets/`:
- `f854f9d8271445c0e86b11271ccccf4c.mp4` (benchmark `@refinedambition_`)
- `8aaaa67bc8c0b8005f09735e3de0bc8c.mp4` (`@alhusaynn` / Suara Berkelas)
- `felix-siauw-0800-0930.mp4` (`1080×1920`, Ust. Felix Siauw × Bangsap)
- `tiktok-bangkit-about-you.mp4` (`1080×1920`, Suara Berkelas — *"Energi Untuk Bangkit"*)

---

## 1. Spesifikasi Teknis Output
- **Resolusi & Frame Rate:** `1080×1920` (9:16), `30fps`, `libx264` (`yuv420p`) + `aac` `48000Hz` stereo.
- **Normalisasi Audio:** `-16 LUFS` (`loudnorm=I=-16:TP=-1.5:LRA=11`) untuk vokal utama; *dynamic ducking* pada BGM.

## 2. Komposisi Kamera & Layout
- **Face Tracking:** Gunakan `track_faces.py` (*scene-cut detection* + *smoothing*) untuk menjaga pembicara tetap di pusat bingkai vertikal saat hard-cut antar kamera.
- **Posisi Teks (Aman dari UI TikTok/Reels):**
  - *Single-speaker headroom luas:* letakkan tumpukan teks di **sepertiga atas** (seperti `tiktok-bangkit-about-you.mp4`).
  - *Close-up wajah penuh:* letakkan tumpukan teks di **sepertiga bawah** di atas area baju/mikrofon (seperti `felix-siauw-0800-0930.mp4`).
- **HUD Minimalis:**
  - Header tipis di atas (`TOPIK / NAMA PEMBICARA`, huruf kapital spasi lebar).
  - Footer tipis di bawah (`♪ JUDUL BGM`).

## 3. Tipografi Kinetik (`@refinedambition_`)
- **Kontras Font:**
  - Kata kunci/emosi: `Montserrat Black` (`900`), ukuran besar (`78–102px`), huruf kapital, `line-height: 0.92`, `letter-spacing: -2px`.
  - Kata sambung/editorial: `Playfair Display Bold Italic` (`700 italic`) atau `Montserrat Bold` ukuran lebih kecil.
- **Palet Warna Aksen:** Putih (`#FFFFFF`), Emas (`#FBBF24`), Merah (`#EF4444`), Ungu Pastel (`#A78BFA`) + `text-shadow` glow halus.
- **Black-Screen Kinetic Cutaway:** Pada kalimat punchline/inti, potong ke layar hitam penuh (`#050507`) dengan teks rata tengah + SFX `boom.mp3` (seperti `tiktok-bangkit-about-you.mp4` & `f854f9d8271445c0e86b11271ccccf4c.mp4`).
- **Ikon/B-Roll Cutaway (Opsional):** Sisipkan ikon grafis emosi (`?`, simbol sederhana) atau klip ilustrasi singkat saat pembicara memberi analogi (seperti `8aaaa67bc8c0b8005f09735e3de0bc8c.mp4`).

---
name: jubaidah-editor
description: Agen Editing Video (Jubaidah) di Ardy AI Agency HQ. Gunakan skill ini untuk membaca brief Sentod di 01_briefs/, mengolah bahan mentah dari 00_raw_assets/ (atau Google Drive terhubung) menjadi video vertikal 9:16 (1080x1920, 30fps) lengkap dengan normalisasi audio & subtitle memakai FFmpeg/Python, memverifikasi hasil via ffprobe, serta menyinkronkan status Jubaidah di office_state.json.
---
# SOP Kerja Jubaidah (Editing Video)

Peran Anda adalah **Jubaidah**, AI Agent Editing Video & Quality Assurance di **Ardy AI Agency HQ**. Ikuti SOP ini secara berurutan agar setiap video siap tayang tanpa error.

---

## Langkah 1 — Masuk Ruang Kerja & Update Kantor 3D

Perbarui `office_state.json` agar Jubaidah berpindah ke `workspace` dengan status `"Edit FFmpeg"`:

```bash
python3 scripts/update_office_state.py \
  --agent jubaidah \
  --room workspace \
  --status "Edit FFmpeg" \
  --task "Mengolah bahan mentah menjadi video 9:16 (1080x1920, 30fps) + subtitle" \
  --mode work \
  --push
```

---

## Langkah 2 — Baca Brief & Kumpulkan Bahan Mentah

1. Baca brief terbaru di folder `01_briefs/` (mis. `01_briefs/brief_YYYYMMDD.md`).
2. Periksa bahan mentah video/audio/gambar di:
   - Folder lokal `00_raw_assets/`, **atau**
   - Folder Google Drive yang terhubung (gunakan CLI `gdrive readonly ls` / `gdrive readonly search` lalu `gdrive readonly download` bila diperlukan).
3. **Jika bahan mentah belum tersedia sama sekali:**
   - Jangan diam atau menghasilkan file kosong.
   - Buat *visual storyboard/slate video* vertikal `1080×1920` (30fps) berbasis teks hook & poin skrip dari brief menggunakan FFmpeg/Python sebagai draft pratinjau, DAN catat dengan jelas di metadata bahwa footage mentah asli dari Bos Ardy masih dibutuhkan bila ingin dirender ulang.

---

## Langkah 3 — Render Video Vertikal 9:16 + Normalisasi Audio + Subtitle

Pastikan `ffmpeg` dan `ffprobe` tersedia di lingkungan.

### Opsi Standar (FFmpeg / Python — Cepat & Andal di Cloud)
1. **Konversi ke 9:16 (`1080×1920`, `30fps`, H.264 `yuv420p`) + Normalisasi Audio (`-16 LUFS`):**
   ```bash
   ffmpeg -y -i "<INPUT_VIDEO>" \
     -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p" \
     -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
     -c:v libx264 -preset medium -crf 20 \
     -c:a aac -b:a 192k -ar 48000 \
     -movflags +faststart \
     02_edited_videos/temp_9x16.mp4
   ```
2. **Siapkan file subtitle `.srt`** dari skrip/transkrip (`02_edited_videos/video_YYYYMMDD.srt`), lalu **burn-in subtitle** ke zona aman vertikal:
   ```bash
   ffmpeg -y -i 02_edited_videos/temp_9x16.mp4 \
     -vf "subtitles=02_edited_videos/video_YYYYMMDD.srt:force_style='FontName=DejaVu Sans,FontSize=16,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=1,Alignment=2,MarginV=120'" \
     -c:v libx264 -preset medium -crf 20 \
     -c:a copy \
     -movflags +faststart \
     02_edited_videos/video_YYYYMMDD.mp4
   ```
   *(Hapus file sementara `temp_9x16.mp4` setelah file final terbentuk.)*

### Opsi Gaya Premium (Opsional)
Jika Bos Ardy meminta gaya *kinetic typography* ala `@refinedambition_` dengan *OpenCV face tracking* + *black-screen cutaway* di Remotion, gunakan juga skill **`editvidio`** lalu simpan hasil akhirnya ke `02_edited_videos/video_YYYYMMDD.mp4`.

---

## Langkah 4 — Wajib Quality Assurance (QA) dengan `ffprobe`

**WAJIB** jalankan pemeriksaan `ffprobe` sebelum menyatakan selesai agar video dipastikan tidak corrupt:

```bash
ffprobe -v error -show_format -show_streams -of json 02_edited_videos/video_YYYYMMDD.mp4
```

Pastikan seluruh kriteria berikut lulus:
- Exit code `0` (file valid, tidak corrupt).
- Resolusi tepat **`1080×1920`** (rasio `9:16`).
- Frame rate ~**`30 fps`** dan codec `h264` (`yuv420p`).
- Durasi > 0 detik sesuai rencana skrip.
- Terdapat stream audio (atau catatan eksplisit jika memang video tanpa suara).
- Simpan ringkasan QA ke `02_edited_videos/video_YYYYMMDD_qa.json` agar dapat dibaca langsung oleh **Bodat**.

---

## Langkah 5 — QA Lulus & Pindah ke Area Ngopi

Setelah QA lulus, perbarui `office_state.json` agar Jubaidah pindah ke `"coffee"` dengan status `"QA Lulus"`:

```bash
python3 scripts/update_office_state.py \
  --agent jubaidah \
  --room coffee \
  --status "QA Lulus" \
  --task "Video 9:16 lulus cek ffprobe di 02_edited_videos/, handoff ke Bodat" \
  --push
```

Lanjutkan estafet ke **Bodat** (`bodat-uploader`) jika berjalan dalam pipeline penuh.

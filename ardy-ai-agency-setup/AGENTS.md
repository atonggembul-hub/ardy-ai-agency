# AGENTS.md — SOP Utama Ardy AI Agency HQ

Dokumen ini adalah buku panduan operasional utama (*Master SOP*) bagi tim AI Agent di **Ardy AI Agency HQ** yang berjalan pada **Google Antigravity Remote (Cloud)** dan terhubung secara real-time dengan visualisasi **Kantor AI Agent 3D**.

- **Repositori GitHub:** `https://github.com/atonggembul-hub/ardy-ai-agency`
- **Kantor AI Agent 3D (Live Visual):** `https://atonggembul-hub.github.io/ardy-ai-agency/`
- **State Real-Time:** `office_state.json` (dibaca langsung oleh Kantor AI Agent 3D)
- **Niche Konten:** **Fleksibel** — selalu ikuti niche/topik yang diminta pada perintah chat harian atau jadwal `/automation`. Jika belum ditentukan saat berjalan otomatis, pilih topik tren paling relevan hari ini dan cantumkan alasannya di dalam brief.

---

## 1. Struktur Tim & Skill

| Agen | Key JSON | Peran | Ruangan Utama | Skill |
| :--- | :--- | :--- | :--- | :--- |
| **Bos Ardy** | `ardy` | Pengawas & CEO (*Human-in-the-Loop*) | `boss` | Pemberi arahan & **ACC final** |
| **Sentod** | `sentod` | Analis Konten & Riset Tren | `workspace` | `.agents/skills/sentod-analis/SKILL.md` |
| **Jubaidah** | `jubaidah` | Editing Video 9:16 & QA Render | `workspace` | `.agents/skills/jubaidah-editor/SKILL.md` |
| **Bodat** | `bodat` | Penulis Caption, Bundling & Uploader | `workspace` | `.agents/skills/bodat-uploader/SKILL.md` |

Untuk orkestrasi penuh satu kali jalan, gunakan juga skill master `.agents/skills/office-ai-agent/SKILL.md`.

---

## 2. Struktur Folder Produksi

```text
ardy-ai-agency/
├── AGENTS.md                       # SOP Utama ini
├── office_state.json               # Status real-time Kantor AI Agent 3D
├── index.html                      # Aplikasi web Kantor AI Agent 3D (GitHub Pages)
├── scripts/
│   └── update_office_state.py      # Helper CLI update status & git push
├── 00_raw_assets/                  # Bahan mentah video/audio/foto (atau dari Google Drive)
├── 01_briefs/                      # Output Sentod: brief_YYYYMMDD.md
├── 02_edited_videos/               # Output Jubaidah: video_YYYYMMDD.mp4 + .srt
├── 03_ready_to_post/               # Output Bodat: paket_YYYYMMDD/
└── .agents/skills/                 # Skill masing-masing agen
```

---

## 3. Protokol Sinkronisasi Kantor AI Agent 3D (`office_state.json`)

Setiap agen **WAJIB** memperbarui `office_state.json` di awal dan di akhir tugasnya menggunakan skrip helper `scripts/update_office_state.py` (dengan `--push` agar perubahan segera tampil di Kantor AI Agent 3D online):

```bash
python3 scripts/update_office_state.py \
  --agent <ardy|sentod|jubaidah|bodat> \
  --room <boss|workspace|meeting|coffee> \
  --status "<Status Singkat Maks 16 Karakter>" \
  --task "<Deskripsi tugas saat ini>" \
  --mode <work|meeting|coffee> \
  --push
```

### Nilai Valid Skema `office_state.json`
- `mode`: `"work"` | `"meeting"` | `"coffee"`
- `room`: `"boss"` (Ruang Bos Ardy) | `"workspace"` (Ruang Kerja AI) | `"meeting"` (Ruang Meeting) | `"coffee"` (Area Ngopi & Lounge)
- `approval_needed`: `true` (menampilkan banner notifikasi ACC Bos Ardy di Kantor 3D) | `false`
- `approval_message`: pesan ringkas lokasi paket & ringkasan konten untuk Bos Ardy.

---

## 4. Pipeline Estafet Produksi Harian

### Tahap 1 — Sentod (`sentod-analis`)
1. Jalankan update status: `sentod` masuk `workspace` (`"Riset Tren"`), `jubaidah` & `bodat` menunggu di `coffee`, `ardy` di `boss` (`"Pantau Cloud"`).
2. Riset **3 topik tren terbaru hari ini** sesuai niche yang diminta melalui web search.
3. Pilih **1 ide terbaik** dengan potensi retensi dan engagement tertinggi.
4. Simpan brief lengkap ke `01_briefs/brief_YYYYMMDD.md` berisi: Judul, Hook 3 detik, Skrip singkat, Arahan visual untuk Jubaidah, Sumber tren, dan Kata kunci SEO.
5. Update status: `sentod` pindah ke `coffee` (`"Selesai Riset"`).

### Tahap 2 — Jubaidah (`jubaidah-editor`)
1. Update status: `jubaidah` masuk `workspace` (`"Edit FFmpeg"`).
2. Baca brief terbaru di `01_briefs/` dan periksa bahan mentah di `00_raw_assets/` (atau folder Google Drive yang terhubung via `gdrive`).
   - *Catatan Fallback:* Jika bahan video mentah belum tersedia di `00_raw_assets/` maupun Google Drive, jangan menggagalkan pipeline secara diam-diam — buat preview visual/slate vertikal `1080×1920` dari naskah brief atau tandai catatan jelas bahwa video masih menunggu footage mentah dari Bos Ardy.
3. Render video vertikal **9:16 (`1080×1920`, `30fps`, H.264 + AAC)**, normalisasi audio ke standar `-16 LUFS` (`loudnorm`), dan tempel subtitle ke `02_edited_videos/video_YYYYMMDD.mp4`.
   - Bila membutuhkan gaya *kinetic typography* ala `@refinedambition_` + *face tracking* Remotion, Jubaidah dapat merujuk pada skill `editvidio`.
4. **Wajib QA dengan `ffprobe`**: pastikan file tidak corrupt, resolusi `1080×1920`, durasi valid, serta track video & audio terbaca normal.
5. Update status: `jubaidah` pindah ke `coffee` (`"QA Lulus"`).

### Tahap 3 — Bodat (`bodat-uploader`)
1. Update status: `bodat` masuk `workspace` (`"Tulis Caption"`).
2. Baca brief Sentod (`01_briefs/brief_YYYYMMDD.md`) dan metadata video hasil QA Jubaidah (`02_edited_videos/`).
3. Tulis **3 variasi caption** (*Santai*, *Edukatif*, *Pancing Komentar*) + **5–8 hashtag** relevan.
4. Kemas seluruh paket siap tayang ke folder `03_ready_to_post/paket_YYYYMMDD/`:
   - `video_final.mp4` (salinan/tautan hasil render terverifikasi)
   - `captions.md` (3 variasi caption + hashtag + rekomendasi jam tayang)
   - `metadata.json` (judul, niche, durasi, resolusi, sumber brief, status ACC)
5. **Tahap 4 — Checkpoint Human-in-the-Loop (WAJIB BERHENTI):**
   - Update `office_state.json`: `approval_needed: true`, `mode: "coffee"`, `bodat` pindah ke `coffee` (`"Tunggu ACC"`), `ardy` tetap di `boss` (`"Perlu ACC 🔔"`), lalu `--push`.
   - Sajikan laporan ringkas hasil kerja Sentod, Jubaidah, dan Bodat kepada **Bos Ardy** di chat dan **BERHENTI**.

### Tahap 5 — Pasca ACC Bos Ardy
- **DILARANG KERAS** mengunggah atau memublikasikan konten secara live sebelum mendapat balas **ACC** eksplisit dari Bos Ardy.
- Setelah Bos Ardy membalas ACC (mis. *"ACC! Bodat silakan upload paket hari ini, lalu semua tim boleh ngopi."*):
  1. Bodat masuk `workspace` (`"Upload Live"`), memproses unggahan/penjadwalan atau mengekspor paket ke folder publikasi yang ditunjuk (mis. Google Drive / platform target), dan mencatat bukti di `03_ready_to_post/paket_YYYYMMDD/published_log.json`.
  2. Setelah selesai, jalankan `python3 scripts/update_office_state.py --set-all-coffee --approval-needed false --push` agar seluruh tim masuk mode **Ngopi** dengan status selesai.

---

## 5. Aturan Keselamatan & Kualitas

1. **Jangan hapus aset mentah** di `00_raw_assets/`.
2. **Jangan pernah commit kredensial/token** ke repositori ini (repositori bersifat **Public** agar Kantor 3D & Live Sync aktif tanpa token).
3. **File video berukuran besar (>50 MB):** simpan file MP4 besar di Google Drive terhubung dan cantumkan link/ID-nya di `metadata.json` agar repositori GitHub tetap ringan dan cepat di-sync.
4. **Selalu commit & push `office_state.json`** setiap pergantian status agar visualisasi Kantor AI Agent 3D tetap akurat.

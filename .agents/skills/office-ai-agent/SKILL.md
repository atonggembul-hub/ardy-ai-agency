---
name: office-ai-agent
description: Orkestrator utama Office AI Agent (Ardy AI Agency HQ) yang menjalankan estafet produksi konten harian lintas 3 agen (Sentod Analis -> Jubaidah Editor -> Bodat Uploader), menyinkronkan status real-time ke Kantor AI Agent 3D melalui office_state.json di repo GitHub atonggembul-hub/ardy-ai-agency, dan berhenti di checkpoint ACC Bos Ardy. Dipicu oleh /office-ai-agent, "jalankan kantor AI", atau "jalankan estafet produksi konten harian".
---
# Skill: office-ai-agent (Ardy AI Agency HQ Orchestrator)

Skill orkestrator ini mengoordinasikan seluruh alur kerja **Ardy AI Agency HQ** sekaligus menjaga agar visualisasi **Kantor AI Agent 3D** tetap sinkron secara real-time di setiap tahapan.

- **Repositori GitHub:** `https://github.com/atonggembul-hub/ardy-ai-agency`
- **Live Kantor AI Agent 3D:** `https://atonggembul-hub.github.io/ardy-ai-agency/`
- **Live State JSON:** `https://atonggembul-hub.github.io/ardy-ai-agency/office_state.json`

---

## Persiapan Repositori

1. Pastikan berada di direktori repositori `ardy-ai-agency` (jika belum ada di workspace, clone dengan `gh repo clone atonggembul-hub/ardy-ai-agency`).
2. Baca `AGENTS.md` sebagai acuan SOP terbaru.
3. Jalankan `git pull --rebase` sebelum memulai estafet agar `office_state.json` dan folder produksi selalu mutakhir.

---

## Alur Estafet Penuh (Sentod → Jubaidah → Bodat → Checkpoint Bos Ardy)

### 1. Inisialisasi Pipeline
- Pindahkan `sentod` ke `workspace`, `jubaidah` & `bodat` ke `coffee`, dan `ardy` ke `boss` (`"Pantau Cloud"`), dengan `approval_needed: false`.

### 2. Jalankan Sentod (`sentod-analis`)
- Ikuti seluruh SOP pada skill **`sentod-analis`**.
- Verifikasi file `01_briefs/brief_YYYYMMDD.md` telah terbuat.
- Commit brief & push update status `sentod` → `coffee` (`"Selesai Riset"`).

### 3. Jalankan Jubaidah (`jubaidah-editor`)
- Ikuti seluruh SOP pada skill **`jubaidah-editor`**.
- Pastikan output video `9:16` (`1080×1920`, `30fps`) tersimpan di `02_edited_videos/video_YYYYMMDD.mp4` dan **lulus verifikasi `ffprobe`** (`02_edited_videos/video_YYYYMMDD_qa.json`).
- Push update status `jubaidah` → `coffee` (`"QA Lulus"`).

### 4. Jalankan Bodat (`bodat-uploader`) & Checkpoint ACC
- Ikuti seluruh SOP pada skill **`bodat-uploader`**.
- Pastikan folder `03_ready_to_post/paket_YYYYMMDD/` lengkap (`captions.md`, `metadata.json`, dan video/link Drive).
- Commit seluruh dokumen brief, QA JSON, caption, metadata, dan `office_state.json` (`approval_needed: true`, `mode: "coffee"`, `bodat` → `coffee` `"Tunggu ACC"`, `ardy` → `boss` `"Perlu ACC 🔔"`), lalu `git push`.
- **WAJIB BERHENTI** dan tampilkan laporan ringkas + link Kantor AI Agent 3D kepada Bos Ardy untuk ACC.

### 5. Mode Khusus Kantor 3D (Opsional)
Jika Bos Ardy hanya meminta perubahan mode kantor tanpa menjalankan produksi:
- **Mode Meeting:** `python3 scripts/update_office_state.py --set-all-meeting --push`
- **Mode Ngopi:** `python3 scripts/update_office_state.py --set-all-coffee --approval-needed false --push`
- **Mode Kerja:** `python3 scripts/update_office_state.py --set-all-work --approval-needed false --push`

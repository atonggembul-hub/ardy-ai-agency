# Ardy AI Agency HQ — Office AI Agent & Kantor 3D

Sistem **Multi-Agent Content Agency** di **Google Antigravity Remote (Cloud)** lengkap dengan visualisasi **Kantor AI Agent 3D Interaktif** yang tersinkronisasi secara real-time melalui `office_state.json`.

## Akses Cepat

- **Kantor AI Agent 3D (Live HQ):** [https://atonggembul-hub.github.io/ardy-ai-agency/](https://atonggembul-hub.github.io/ardy-ai-agency/)
- **Live JSON State (GitHub Pages):** [https://atonggembul-hub.github.io/ardy-ai-agency/office_state.json](https://atonggembul-hub.github.io/ardy-ai-agency/office_state.json)
- **Live JSON State (GitHub Raw):** [https://raw.githubusercontent.com/atonggembul-hub/ardy-ai-agency/main/office_state.json](https://raw.githubusercontent.com/atonggembul-hub/ardy-ai-agency/main/office_state.json)

---

## Tim AI Agent

| Agen | Peran | Skill |
| :--- | :--- | :--- |
| **Bos Ardy** (`ardy`) | Pengawas & CEO (*Human-in-the-Loop*) | Review & ACC publikasi |
| **Sentod** (`sentod`) | Analis Konten & Riset Tren | `.agents/skills/sentod-analis/SKILL.md` |
| **Jubaidah** (`jubaidah`) | Editing Video 9:16 & QA `ffprobe` | `.agents/skills/jubaidah-editor/SKILL.md` |
| **Bodat** (`bodat`) | Penulis Caption, Bundler & Uploader | `.agents/skills/bodat-uploader/SKILL.md` |
| **Orchestrator** | Koordinator Estafet & Sync Kantor 3D | `.agents/skills/office-ai-agent/SKILL.md` |

---

## Cara Menjalankan di Google Antigravity Remote

### 1. Hubungkan Repositori ke Remote Project
1. Buka **`antigravity.google.com`** → **Create Project** → **New Remote Project**.
2. Pada bagian **Attach Resource**, hubungkan repositori GitHub **`atonggembul-hub/ardy-ai-agency`** (dan Google Drive jika menyimpan bahan mentah video).

### 2. Pemicu Manual (1 Kalimat di Chat)
```text
Jalankan estafet produksi konten harian untuk niche [ISI NICHE ANDA] menggunakan skill sentod-analis, jubaidah-editor, dan bodat-uploader. Setelah siap tayang, berhenti dan laporkan ke saya untuk ACC.
```

### 3. Jadwal Otomatis Harian (`/automation`)
Ketik `/automation` di chat Remote Project, pilih jadwal **Daily** (`08:00 WIB` / `Asia/Jakarta`), lalu masukkan tugas:
```text
Jalankan pipeline harian menggunakan skill sentod-analis, jubaidah-editor, dan bodat-uploader sesuai aturan AGENTS.md, update office_state.json, lalu laporkan hasilnya untuk ACC Bos Ardy.
```

### 4. Memberi ACC dari HP/Laptop
Pantau pergerakan tim di **[Kantor AI Agent 3D](https://atonggembul-hub.github.io/ardy-ai-agency/)**. Saat banner **Menunggu ACC Bos Ardy** muncul, cek laporan lalu balas:
```text
ACC! Bodat silakan upload paket hari ini, lalu semua tim boleh ngopi.
```

---

## Helper CLI Update Kantor 3D

```bash
# Contoh: Sentod mulai riset tren
python3 scripts/update_office_state.py \
  --agent sentod --room workspace --status "Riset Tren" \
  --task "Riset 3 topik viral hari ini" --mode work --push

# Contoh: Bodat selesai & meminta ACC Bos Ardy
python3 scripts/update_office_state.py \
  --agent bodat --room coffee --status "Tunggu ACC" \
  --task "Paket siap di 03_ready_to_post/" \
  --mode coffee --approval-needed true \
  --approval-message "Paket konten hari ini siap tayang! Menunggu ACC Bos Ardy." \
  --push

# Contoh: Semua tim istirahat ngopi setelah ACC selesai
python3 scripts/update_office_state.py --set-all-coffee --approval-needed false --push
```

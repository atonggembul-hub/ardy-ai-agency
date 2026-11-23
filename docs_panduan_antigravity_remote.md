# Panduan Memulai di Google Antigravity Remote (Cloud)

## Jawaban Singkat: Apakah Cukup "Drop Skill" Tanpa Prompt?

**Tidak bisa jalan sendiri hanya dengan di-drop.**  
Di Google Antigravity, **Skill (`SKILL.md`) sifatnya seperti "Buku SOP / Keahlian"** yang pasif—agen baru akan membacanya ketika ada **pemicu (trigger)**, baik berupa:
1. **Satu kalimat perintah di chat** (pemicu manual), **atau**
2. **Jadwal Otomatis (`/automation` atau `/schedule`)** agar agen "bangun" sendiri setiap hari tanpa Anda mengetik chat lagi.

> **Penting Khusus Mode Remote (Cloud):**  
> Remote Agents yang berjalan di *cloud* Google **tidak dapat membaca Skill lokal yang tersimpan di komputer Anda** (`~/.gemini/config/skills/`). Supaya terbaca di *cloud*, file `AGENTS.md` dan folder `.agents/skills/` **harus berada di dalam GitHub Repository** (atau file proyek) yang Anda lampirkan (*Attach Resource*) ke **Remote Project**.

---

## Langkah-Langkah Memulai dari Nol sampai Jalan Otomatis

### Langkah 1: Siapkan Struktur Skill di GitHub Repository Anda
Buat satu repositori GitHub baru (boleh **Private**), misalnya bernama `ardy-ai-agency`. Di dalamnya, susun folder dan file seperti ini:

```text
ardy-ai-agency/
├── AGENTS.md                              <-- SOP Utama (dari dokumen sebelumnya)
├── office_state.json                      <-- Status real-time untuk Kantor 3D
└── .agents/
    └── skills/
        ├── sentod-analis/
        │   └── SKILL.md                   <-- Skill khusus Sentod
        ├── jubaidah-editor/
        │   └── SKILL.md                   <-- Skill khusus Jubaidah
        └── bodat-uploader/
            └── SKILL.md                   <-- Skill khusus Bodat
```

Berikut contoh isi masing-masing file `SKILL.md` yang bisa langsung Anda salin (*drop*):

#### 1. `.agents/skills/sentod-analis/SKILL.md`
```markdown
---
name: sentod-analis
description: Agen Analis Konten (Sentod). Gunakan skill ini untuk riset tren viral, analisis kompetitor, dan membuat brief produksi harian ke folder 01_briefs/.
---
# SOP Kerja Sentod (Analis Konten)
1. Ubah status `sentod` di `office_state.json` menjadi `"Riset Tren"` (`room: "workspace"`).
2. Cari 3 topik tren terbaru hari ini sesuai niche Bos Ardy menggunakan web search.
3. Pilih 1 ide terbaik dan buat file `01_briefs/brief_YYYYMMDD.md` berisi: Judul, Hook 3 detik, Skrip singkat, Arahan visual untuk Jubaidah, dan Kata kunci.
4. Setelah selesai, ubah status `sentod` di `office_state.json` menjadi `"Selesai Riset"` (`room: "coffee"`).
```

#### 2. `.agents/skills/jubaidah-editor/SKILL.md`
```markdown
---
name: jubaidah-editor
description: Agen Editing Video (Jubaidah). Gunakan skill ini untuk mengolah bahan mentah dari 00_raw_assets/ menjadi video vertikal 9:16 lengkap dengan subtitle menggunakan FFmpeg/Python.
---
# SOP Kerja Jubaidah (Editing Video)
1. Ubah status `jubaidah` di `office_state.json` menjadi `"Edit FFmpeg"` (`room: "workspace"`).
2. Baca brief terbaru di `01_briefs/` dan ambil bahan video di `00_raw_assets/` (atau Google Drive terhubung).
3. Render video format 9:16 (1080x1920, 30fps), normalisasi audio, dan tempel subtitle ke `02_edited_videos/`.
4. Wajib cek hasil render memakai `ffprobe` agar dipastikan tidak corrupt.
5. Setelah selesai, ubah status `jubaidah` di `office_state.json` menjadi `"QA Lulus"` (`room: "coffee"`).
```

#### 3. `.agents/skills/bodat-uploader/SKILL.md`
```markdown
---
name: bodat-uploader
description: Agen Penulis Caption & Uploader (Bodat). Gunakan skill ini untuk menulis caption, hashtag, membundel paket tayang di 03_ready_to_post/, dan mengunggah setelah ACC Bos Ardy.
---
# SOP Kerja Bodat (Caption & Uploader)
1. Ubah status `bodat` di `office_state.json` menjadi `"Tulis Caption"` (`room: "workspace"`).
2. Baca brief Sentod dan metadata video Jubaidah, lalu buat 3 variasi caption (Santai, Edukatif, Pancing Komentar) + 5-8 hashtag.
3. Simpan paket siap tayang di `03_ready_to_post/paket_YYYYMMDD/`.
4. Set `"approval_needed": true` di `office_state.json`, ubah `room` ke `"coffee"`, dan BERHENTI untuk meminta ACC Bos Ardy sebelum publikasi live.
```

---

### Langkah 2: Buat Remote Project di Google Antigravity
1. Buka **`antigravity.google.com`** lewat browser (HP atau laptop), atau buka aplikasi Google Antigravity Desktop. *(Pastikan login dengan akun Google personal yang berlangganan Google AI Pro atau Ultra).*
2. Di sidebar kiri bagian **Projects**, klik **`+`** (atau **Create Project**) lalu pilih **New Remote Project** (pastikan pilih mode **Remote Agents / Cloud**, bukan *Remote Control*).
3. Pada bagian **Add Resource / Attach**:
   - Hubungkan **GitHub Repository** `ardy-ai-agency` yang baru Anda buat.
   - Hubungkan juga **Google Drive** (folder tempat Anda menyimpan bahan mentah video jika ada).
4. Beri nama proyek (misalnya: `Ardy-AI-Agency-Cloud`) lalu klik **Create**.

---

### Langkah 3: Pilih Cara Memulai (Cukup 1x di Awal!)

Sekarang semua *Skill* sudah terpasang di proyek *cloud*. Anda tidak perlu mengetik prompt panjang lebar lagi—pilih salah satu cara berikut:

#### Opsi A — Cara Cepat (1 Kalimat Pemicu di Chat)
Jika ingin langsung tes kerja sekarang, cukup ketik 1 kalimat pendek ini di chat Remote Project Anda:
```text
Jalankan estafet produksi konten harian untuk niche [ISI NICHE ANDA] menggunakan skill sentod-analis, jubaidah-editor, dan bodat-uploader. Setelah siap tayang, berhenti dan laporkan ke saya untuk ACC.
```
Begitu Anda tekan **Enter**, Anda boleh langsung **menutup browser atau mematikan laptop**. Proses akan tetap berjalan sampai selesai di *cloud* Google.

#### Opsi B — Otomatis Penuh Tanpa Chat Harian (Pakai `/automation`)
Jika Anda ingin tim AI bekerja otomatis setiap hari (misalnya setiap jam 08:00 WIB) tanpa Anda mengetik chat sama sekali:
1. Di kotak chat Remote Project, ketik perintah:
   ```text
   /automation
   ```
   *(Atau buka tab **Automations** lalu klik **Create with Prompt**).*
2. Antigravity akan menanyakan beberapa hal singkat (Anda tinggal klik/jawab):
   - **Cadence (Jadwal):** Pilih **Daily** (Harian).
   - **Jam & Zona Waktu:** Ketik `08:00 WIB` (`Asia/Jakarta`).
   - **Tugas (Task):** Ketik: *"Jalankan pipeline harian menggunakan skill sentod-analis, jubaidah-editor, dan bodat-uploader sesuai aturan AGENTS.md, update office_state.json, lalu laporkan hasilnya untuk ACC Bos Ardy."*
3. Saat ditanya **"Execute a test run now to configure permissions?"**, pilih **Yes (Recommended)**. Ini sangat penting agar izin akses (*permissions*) tercatat dan jadwal otomatis besok tidak macet.
4. Buka tab **Automations**, lalu nyalakan (*Enable*) jadwal tersebut.

---

### Langkah 4: Rutinitas Anda Sebagai Bos Ardy (Cukup Pantau dari HP)
Setelah langkah 3 selesai, Anda tidak perlu lagi repot mengatur apa pun:
- **Setiap hari**, Sentod → Jubaidah → Bodat berjalan sendiri di *cloud* Google.
- **Pantau visual** pergerakan mereka di aplikasi **Kantor AI Agent 3D** (via URL `office_state.json`).
- **Cek laporan & beri ACC** lewat browser HP di `antigravity.google.com`. Jika sudah cocok, cukup balas singkat:
  ```text
  ACC! Bodat silakan upload paket hari ini, lalu semua tim boleh ngopi.
  ```
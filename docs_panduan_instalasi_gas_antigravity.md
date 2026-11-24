# Panduan Instalasi Lengkap: Kantor AI Agent 3D (Google Apps Script) + Google Antigravity Remote

Panduan ini dirancang berurutan dari **Langkah 1 sampai Selesai** agar:
1. **Kantor AI Agent 3D** (dengan fitur klik karakter untuk chat & tombol ACC) tayang gratis di **Google Apps Script** dan bisa dibuka dari HP maupun laptop.
2. **Sentod, Jubaidah, dan Bodat** bekerja otomatis 100% di *cloud* **Google Antigravity Remote** tanpa menyalakan komputer Anda.
3. Keduanya tersambung **2 arah**: pergerakan & status AI tampil *live* di Kantor 3D, sementara pesan chat atau ACC yang Anda ketik di Kantor 3D bisa langsung dibaca oleh tim AI di Antigravity.

---

## Persiapan Awal (Ceklis 3 Menit)
Pastikan Anda sudah menyiapkan:
- [ ] **Akun Google** (disarankan akun yang sudah memiliki akses **Google Antigravity** / Google AI Pro atau Ultra).
- [ ] **Akun GitHub** (gratis di [github.com](https://github.com)) untuk menyimpan file `AGENTS.md`, `SKILL.md`, dan skrip penghubung.
- [ ] **Token Rahasia Buatan Sendiri** (misalnya: `ARDY_HQ_2026_RAHASIA`). Catat token ini karena akan dipakai di **Apps Script** dan **Antigravity**.

---

# BAGIAN 1: Instalasi Kantor 3D & Jembatan Data di Google Apps Script

## Langkah 1.1 — Buat Proyek Baru
1. Buka **[script.google.com](https://script.google.com)** dan login dengan akun Google Anda.
2. Klik tombol **+ New project** (Proyek baru) di kiri atas.
3. Klik judul *Untitled project* di atas, lalu ubah menjadi **`Ardy-AI-Office-3D`**.

## Langkah 1.2 — Pasang Backend `Code.gs` (Mendukung Live Sync & Chat Bos Ardy)
1. Buka file **`Code.gs`** di panel kiri, hapus seluruh isi bawaannya.
2. Salin dan tempel seluruh kode berikut ke **`Code.gs`**, lalu ganti nilai `SECRET_TOKEN` sesuai token rahasia Anda:

```javascript
// =========================================================================
// ARDY AI AGENCY HQ — GOOGLE APPS SCRIPT BRIDGE & 3D OFFICE HOST (2 ARAH)
// =========================================================================

// WAJIB GANTI dengan kata sandi rahasia Anda sendiri (samakan dengan di Antigravity)
const SECRET_TOKEN = 'ARDY_HQ_2026_RAHASIA';

const STATE_KEY = 'ARDY_OFFICE_STATE_JSON';
const COMMAND_KEY = 'ARDY_BOSS_COMMAND_JSON';

const DEFAULT_STATE = {
  mode: 'work',
  updated_at: new Date().toISOString(),
  approval_needed: false,
  approval_message: '',
  agents: {
    ardy:     { status: 'Mengawasi',     room: 'boss',      task: 'Memantau sistem cloud Antigravity' },
    sentod:   { status: 'Standby',       room: 'workspace', task: 'Menunggu jadwal riset' },
    jubaidah: { status: 'Standby',       room: 'workspace', task: 'Menunggu brief video' },
    bodat:    { status: 'Standby',       room: 'workspace', task: 'Menunggu hasil render' }
  }
};

/**
 * Menangani tampilan Kantor 3D di browser & permintaan GET API dari Antigravity
 */
function doGet(e) {
  const params = (e && e.parameter) ? e.parameter : {};
  const api = params.api || '';

  // 1. Cek status JSON terbaru (?api=state)
  if (api === 'state') {
    return ContentService
      .createTextOutput(getOfficeStateString())
      .setMimeType(ContentService.MimeType.JSON);
  }

  // 2. Antigravity mengecek apakah ada chat/ACC baru dari Bos Ardy (?api=command&token=...)
  if (api === 'command') {
    if ((params.token || '') !== SECRET_TOKEN) {
      return jsonResponse({ ok: false, error: 'Token tidak valid' });
    }
    const props = PropertiesService.getScriptProperties();
    const raw = props.getProperty(COMMAND_KEY) || JSON.stringify({ command: null, status: 'none' });
    return ContentService
      .createTextOutput(raw)
      .setMimeType(ContentService.MimeType.JSON);
  }

  // 3. Default: Tampilkan aplikasi Kantor AI Agent 3D (Index.html)
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Kantor AI Agent 3D — Ardy HQ')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
}

/**
 * Menerima update status agen ATAU konfirmasi selesai perintah (ack) dari Google Antigravity
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ ok: false, error: 'Body JSON kosong' });
    }

    const payload = JSON.parse(e.postData.contents);
    if (payload.token !== SECRET_TOKEN) {
      return jsonResponse({ ok: false, error: 'Unauthorized: token tidak cocok' });
    }

    const props = PropertiesService.getScriptProperties();

    // Jika Antigravity mengirim konfirmasi bahwa chat/perintah Bos Ardy sudah dieksekusi
    if (payload.action === 'ack_command') {
      const currentRaw = props.getProperty(COMMAND_KEY);
      if (currentRaw) {
        const currentCmd = JSON.parse(currentRaw);
        currentCmd.status = 'done';
        currentCmd.done_at = new Date().toISOString();
        props.setProperty(COMMAND_KEY, JSON.stringify(currentCmd));
      }
      return jsonResponse({ ok: true, message: 'Perintah Bos Ardy ditandai selesai (done)' });
    }

    // Default: Simpan update status Kantor 3D (hapus token sebelum disimpan)
    delete payload.token;
    payload.updated_at = new Date().toISOString();
    props.setProperty(STATE_KEY, JSON.stringify(payload));

    return jsonResponse({
      ok: true,
      message: 'Status Kantor 3D berhasil diperbarui',
      updated_at: payload.updated_at
    });
  } catch (err) {
    return jsonResponse({ ok: false, error: err.message });
  }
}

/**
 * Dipanggil otomatis oleh Index.html setiap 5 detik (google.script.run.getOfficeState)
 */
function getOfficeState() {
  return JSON.parse(getOfficeStateString());
}

/**
 * Dipanggil otomatis saat Bos Ardy mengirim Chat ke Karakter atau klik "Kirim ACC Langsung"
 */
function sendBossCommand(commandText) {
  const props = PropertiesService.getScriptProperties();
  const cmdPayload = {
    command: String(commandText || '').trim(),
    created_at: new Date().toISOString(),
    status: 'pending'
  };
  props.setProperty(COMMAND_KEY, JSON.stringify(cmdPayload));
  return { ok: true, saved: cmdPayload };
}

function getOfficeStateString() {
  const props = PropertiesService.getScriptProperties();
  return props.getProperty(STATE_KEY) || JSON.stringify(DEFAULT_STATE);
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```
3. Tekan **`Ctrl + S`** (ikon disket) untuk menyimpan `Code.gs`.

## Langkah 1.3 — Pasang File Kantor 3D (`Index.html`)
1. Di panel kiri Apps Script sebelah tulisan **Files**, klik ikon **`+`** -> pilih **HTML**.
2. Beri nama persis: **`Index`** *(huruf besar `I`, nanti otomatis menjadi `Index.html`)*.
3. Hapus seluruh kode bawaan di `Index.html`.
4. Buka file **`index.html`** (*Kantor AI Agent 3D - Ardy HQ*) yang sudah dibuat di sesi ini, salin seluruh kodenya mulai dari baris **`<!DOCTYPE html>`** sampai **`</html>`** *(pastikan tidak ikut menyalin tanda backtick ` ``` ` jika ada)*, lalu tempel ke **`Index.html`** di Apps Script.
5. Tekan **`Ctrl + S`** untuk menyimpan.

## Langkah 1.4 — Deploy Web App & Dapatkan URL
1. Klik tombol biru **Deploy** (pojok kanan atas) -> pilih **New deployment**.
2. Klik ikon gerigi (**Select type**) -> pilih **Web app**.
3. Isi pengaturan persis seperti ini:
   - **Description:** `Ardy HQ 3D v1`
   - **Execute as:** `Me` *(akun Google Anda)*
   - **Who has access:** `Anyone` *(WAJIB `Anyone` agar Google Antigravity cloud bisa mengirim data tanpa terblokir layar login; keamanan tetap dikunci oleh `SECRET_TOKEN`)*.
4. Klik **Deploy** -> klik **Authorize access** -> pilih akun Google Anda.
   - *Jika muncul layar peringatan "Google hasn't verified this app":* klik **Advanced** (Lanjutan) -> klik **Go to Ardy-AI-Office-3D (unsafe)** -> klik **Allow** (Izinkan). *(Ini wajar untuk skrip pribadi yang Anda buat sendiri).*
5. **Salin Web App URL** yang muncul (berakhiran `/exec`), contohnya:
   ```text
   https://script.google.com/macros/s/AKfycbxxxxxxxxxxxxxxxxxxx/exec
   ```
6. **Uji coba sekarang:** Buka URL `/exec` tersebut di tab browser baru atau di HP Anda!
   - Pastikan badge di kiri atas berubah menjadi hijau **`GAS Live`**.
   - Coba klik salah satu karakter (misalnya **Sentod**), lalu kirim chat tes: `"Riset tren AI hari ini"`. Jika muncul notifikasi `☁️ Pesan ke Sentod tersimpan di Apps Script!`, berarti **Bagian 1 SUKSES 100%!**

> **Tips Penting:** Setiap kali nanti Anda mengedit `Code.gs` atau `Index.html`, perubahan **tidak akan aktif** sebelum Anda klik **Deploy -> Manage deployments -> klik ikon Pensil (Edit) -> Version: pilih `New version` -> klik Deploy**. (URL `/exec` akan tetap sama, tidak berubah).

---

# BAGIAN 2: Menyiapkan Repositori GitHub (Otak, Skill, & Skrip Jembatan)

Google Antigravity Remote membutuhkan repositori GitHub agar aturan tim (`AGENTS.md`), keahlian agen (`SKILL.md`), dan skrip penghubung ke Kantor 3D tersimpan permanen di *cloud*.

## Langkah 2.1 — Buat Repositori GitHub
1. Buka **[github.com/new](https://github.com/new)**.
2. Isi **Repository name**: `ardy-ai-agency`.
3. Pilih **Private** (agar data & SOP Anda tetap aman/pribadi).
4. Centang **Add a README file**, lalu klik **Create repository**.

## Langkah 2.2 — Buat Struktur Folder & File Berikut
Anda bisa membuatnya langsung di browser GitHub (klik **Add file -> Create new file**, lalu ketik path lengkap dengan garis miring `/`, misalnya `.agents/skills/sentod-analis/SKILL.md`):

```text
ardy-ai-agency/
├── AGENTS.md
├── scripts/
│   └── office_bridge.py
└── .agents/
    └── skills/
        ├── sentod-analis/
        │   └── SKILL.md
        ├── jubaidah-editor/
        │   └── SKILL.md
        └── bodat-uploader/
            └── SKILL.md
```

### File 1: `AGENTS.md`
```markdown
# ARDY AI AGENCY — AUTONOMOUS CLOUD WORKSPACE RULES

## 1. Struktur Tim
Sistem ini berjalan 100% di cloud sandbox Google Antigravity untuk **Ardy AI Agency**:
- **Bos Ardy (Pengawas / CEO):** Memberi arahan strategi dan ACC publikasi.
- **Sentod (`sentod-analis`):** Riset tren viral & menyusun brief ke `01_briefs/`.
- **Jubaidah (`jubaidah-editor`):** Edit video vertikal 9:16 + subtitle pakai FFmpeg/Python ke `02_edited_videos/`.
- **Bodat (`bodat-uploader`):** Tulis 3 variasi caption SEO + hashtag & bundel ke `03_ready_to_post/`.

## 2. Integrasi Wajib dengan Kantor 3D (Google Apps Script)
1. **Cek Perintah Bos Ardy di Awal Sesi:** Sebelum bekerja, jalankan `python3 scripts/office_bridge.py --check-command`. Jika ada perintah berstatus `"pending"` dari chat Kantor 3D atau ACC Bos Ardy, prioritaskan untuk langsung mengeksekusinya, lalu jalankan `python3 scripts/office_bridge.py --ack-command`.
2. **Update Live Pergerakan 3D:** Setiap kali Sentod, Jubaidah, atau Bodat berpindah tahap pekerjaan (mulai kerja, meeting, selesai/ngopi, atau menunggu ACC), WAJIB jalankan `python3 scripts/office_bridge.py --push ...` agar karakter di Kantor 3D Bos Ardy bergerak secara real-time.

## 3. Aturan Checkpoint & ACC
- Kerjakan otomatis tanpa bertanya: riset, buat brief, edit/render video FFmpeg, QA `ffprobe`, dan penulisan draf caption.
- **WAJIB BERHENTI & MINTA ACC BOS ARDY** sebelum melakukan live publish ke media sosial publik (set `--approval-needed` pada `office_bridge.py` dan kirim ringkasan singkat siap baca di HP).
```

### File 2: `scripts/office_bridge.py` (Jembatan 2 Arah Antigravity <-> Kantor 3D)
```python
#!/usr/bin/env python3
"""
Jembatan 2 Arah Google Antigravity Remote <-> Kantor 3D Google Apps Script.
Menggunakan Environment Variables:
  - GAS_OFFICE_URL   : Web App URL Apps Script (/exec)
  - GAS_OFFICE_TOKEN : SECRET_TOKEN yang sama persis dengan di Code.gs
"""
import argparse
import json
import os
import sys
import requests

GAS_URL = os.environ.get("GAS_OFFICE_URL", "").strip()
GAS_TOKEN = os.environ.get("GAS_OFFICE_TOKEN", "").strip()
LOCAL_STATE_FILE = "office_state.json"

DEFAULT_STATE = {
    "mode": "work",
    "approval_needed": False,
    "approval_message": "",
    "agents": {
        "ardy":     {"status": "Mengawasi",     "room": "boss",      "task": "Memantau cloud Antigravity"},
        "sentod":   {"status": "Standby",       "room": "workspace", "task": "Siap riset tren"},
        "jubaidah": {"status": "Standby",       "room": "workspace", "task": "Siap edit video"},
        "bodat":    {"status": "Standby",       "room": "workspace", "task": "Siap tulis caption"}
    }
}

def check_env():
    if not GAS_URL or not GAS_TOKEN:
        print("ERROR: GAS_OFFICE_URL atau GAS_OFFICE_TOKEN belum diset di Environment Variables!", file=sys.stderr)
        sys.exit(1)

def load_local_state():
    if os.path.exists(LOCAL_STATE_FILE):
        try:
            with open(LOCAL_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))

def save_local_state(state):
    with open(LOCAL_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def push_state(state):
    check_env()
    save_local_state(state)
    payload = dict(state)
    payload["token"] = GAS_TOKEN
    resp = requests.post(GAS_URL, json=payload, timeout=25, allow_redirects=True)
    resp.raise_for_status()
    print("PUSH OK:", resp.text)

def check_boss_command():
    check_env()
    resp = requests.get(GAS_URL, params={"api": "command", "token": GAS_TOKEN}, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    print(resp.text)

def ack_boss_command():
    check_env()
    resp = requests.post(GAS_URL, json={"token": GAS_TOKEN, "action": "ack_command"}, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    print("ACK OK:", resp.text)

def main():
    parser = argparse.ArgumentParser(description="Bridge Kantor 3D Ardy HQ")
    parser.add_argument("--test", action="store_true", help="Kirim status uji coba ke Kantor 3D")
    parser.add_argument("--check-command", action="store_true", help="Cek chat/ACC terbaru dari Bos Ardy")
    parser.add_argument("--ack-command", action="store_true", help="Tandai perintah Bos Ardy sudah selesai")
    parser.add_argument("--agent", choices=["ardy", "sentod", "jubaidah", "bodat"], help="Agen yang diupdate")
    parser.add_argument("--room", choices=["boss", "workspace", "meeting", "coffee"], help="Ruangan agen")
    parser.add_argument("--status", type=str, help="Label status singkat (max 15 huruf)")
    parser.add_argument("--task", type=str, help="Deskripsi tugas agen saat ini")
    parser.add_argument("--mode", choices=["work", "meeting", "coffee"], help="Mode global kantor")
    parser.add_argument("--approval-needed", choices=["true", "false"], help="Tampilkan banner ACC Bos Ardy")
    parser.add_argument("--approval-message", type=str, help="Pesan banner ACC Bos Ardy")
    args = parser.parse_args()

    if args.check_command:
        check_boss_command()
        return

    if args.ack_command:
        ack_boss_command()
        return

    state = load_local_state()

    if args.test:
        state["mode"] = "meeting"
        state["approval_needed"] = False
        for k, st in [("ardy", "Tes Koneksi"), ("sentod", "Online Cloud"), ("jubaidah", "Online Cloud"), ("bodat", "Online Cloud")]:
            state["agents"][k] = {"status": st, "room": "meeting", "task": "Koneksi Antigravity <-> Apps Script berhasil!"}
        push_state(state)
        return

    if args.mode:
        state["mode"] = args.mode
    if args.approval_needed is not None:
        state["approval_needed"] = (args.approval_needed == "true")
    if args.approval_message is not None:
        state["approval_message"] = args.approval_message

    if args.agent:
        ag = state["agents"].get(args.agent, {})
        if args.room:
            ag["room"] = args.room
        if args.status:
            ag["status"] = args.status
        if args.task is not None:
            ag["task"] = args.task
        state["agents"][args.agent] = ag

    push_state(state)

if __name__ == "__main__":
    main()
```

### File 3: `.agents/skills/sentod-analis/SKILL.md`
```markdown
---
name: sentod-analis
description: Agen Analis Konten (Sentod). Gunakan untuk riset tren viral, analisis kompetitor, dan menyusun brief konten ke 01_briefs/.
---
# SOP Kerja Sentod
1. Jalankan:
   `python3 scripts/office_bridge.py --agent sentod --room workspace --status "Riset Tren" --task "Mencari tren viral hari ini" --mode work`
2. Lakukan web search sesuai niche Bos Ardy, pilih 1-3 ide terbaik, dan simpan brief lengkap (Judul, Hook 3 detik, Skrip, Arahan Visual) ke `01_briefs/brief_YYYYMMDD.md`.
3. Setelah selesai, jalankan:
   `python3 scripts/office_bridge.py --agent sentod --room coffee --status "Selesai Riset" --task "Ngopi santai menunggu siklus berikutnya"`
```

### File 4: `.agents/skills/jubaidah-editor/SKILL.md`
```markdown
---
name: jubaidah-editor
description: Agen Editing Video (Jubaidah). Gunakan untuk edit video 9:16, normalisasi audio, dan auto-subtitle memakai FFmpeg ke 02_edited_videos/.
---
# SOP Kerja Jubaidah
1. Jalankan:
   `python3 scripts/office_bridge.py --agent jubaidah --room workspace --status "Edit 9:16" --task "Render FFmpeg & subtitle"`
2. Baca brief terbaru di `01_briefs/` dan olah bahan video dari `00_raw_assets/` (atau Google Drive terhubung) ke rasio 9:16 (1080x1920, 30fps) di `02_edited_videos/`.
3. Verifikasi hasil output memakai `ffprobe` (pastikan ada video+audio dan tidak corrupt).
4. Setelah lulus QA, jalankan:
   `python3 scripts/office_bridge.py --agent jubaidah --room coffee --status "QA Lulus" --task "Render selesai, istirahat di Coffee Bar"`
```

### File 5: `.agents/skills/bodat-uploader/SKILL.md`
```markdown
---
name: bodat-uploader
description: Agen Penulis Caption & Uploader (Bodat). Gunakan untuk menulis 3 variasi caption SEO + hashtag, membundel ke 03_ready_to_post/, dan mempublikasikan setelah ACC Bos Ardy.
---
# SOP Kerja Bodat
1. Jalankan:
   `python3 scripts/office_bridge.py --agent bodat --room workspace --status "Tulis Caption" --task "Menulis 3 variasi caption & hashtag"`
2. Buat 3 variasi caption (Santai, Edukatif, Pancing Komentar) + 5-8 hashtag relevan dan simpan bersama video final di `03_ready_to_post/paket_YYYYMMDD/`.
3. Hentikan sebelum upload live dan panggil banner ACC Bos Ardy di Kantor 3D:
   `python3 scripts/office_bridge.py --agent bodat --room coffee --status "Tunggu ACC" --task "Siap upload setelah ACC Bos Ardy" --mode coffee --approval-needed true --approval-message "Paket konten hari ini siap di 03_ready_to_post/. Menunggu ACC Bos Ardy!"`
4. Hanya jalankan upload/penjadwalan setelah Bos Ardy memberi ACC (baik lewat chat Antigravity maupun tombol ACC di Kantor 3D).
```

---

# BAGIAN 3: Instalasi & Aktivasi di Google Antigravity Remote

## Langkah 3.1 — Buat Remote Project (Cloud Sandbox)
1. Buka **[antigravity.google.com](https://antigravity.google.com)** (lewat browser laptop atau HP) dan login dengan akun Google Anda.
2. Di panel kiri bagian **Projects**, klik **`+` / Create Project**.
3. Pilih mode **New Remote Project (Remote Agents / Cloud)** — *bukan Remote Control lokal*.
4. Beri nama proyek: **`Ardy-AI-Agency-Cloud`**.

## Langkah 3.2 — Hubungkan GitHub & Google Drive
Pada bagian **Attach Resources / Integrations** saat membuat proyek (atau di menu *Project Settings*):
1. **GitHub:** Sambungkan repositori **`ardy-ai-agency`** yang baru Anda buat di Bagian 2.
2. **Google Drive (Opsional tapi Disarankan):** Sambungkan folder Google Drive tempat Anda meletakkan bahan mentah video (*raw footage*) dan hasil arsip.

## Langkah 3.3 — Pasang Environment Variables / Secrets (PENTING!)
Agar `scripts/office_bridge.py` bisa mengirim status ke Kantor 3D tanpa membocorkan token di GitHub:
1. Buka menu **Settings -> Environment Variables / Secrets** di Remote Project Google Antigravity Anda.
2. Tambahkan **2 variabel** berikut:
   - **`GAS_OFFICE_URL`** = tempel Web App URL `/exec` Anda dari Langkah 1.4.
   - **`GAS_OFFICE_TOKEN`** = tempel `SECRET_TOKEN` Anda (harus **sama persis** dengan yang di `Code.gs`, contoh: `ARDY_HQ_2026_RAHASIA`).
3. Klik **Save**.

## Langkah 3.4 — Jalankan Prompt Inisialisasi & Uji Koneksi (Cukup 1x)
Buka kotak chat di Remote Project Anda, lalu kirim prompt ini untuk menyiapkan *sandbox* Linux sekaligus mengetes apakah Kantor 3D Anda langsung bergerak:

```text
Halo tim Ardy AI Agency! Saya Bos Ardy.
Tolong lakukan instalasi awal di cloud sandbox ini:
1. Buat folder kerja: 00_raw_assets, 01_briefs, 02_edited_videos, 03_ready_to_post, 04_published_archive, dan logs.
2. Pastikan python3, library requests, dan ffmpeg sudah terpasang (install jika belum ada).
3. Jalankan tes koneksi 2 arah ke Kantor 3D Apps Script saya dengan perintah:
   - python3 scripts/office_bridge.py --test
   - python3 scripts/office_bridge.py --check-command
4. Laporkan hasilnya secara singkat.
```

**Cek hasil tes Anda:** Buka kembali tab **Kantor AI Agent 3D** (URL Apps Script `/exec`) Anda! Dalam waktu ≤ 5 detik, Anda akan melihat **Bos Ardy, Sentod, Jubaidah, dan Bodat langsung berjalan berkumpul ke Ruang Meeting** dengan status `"Online Cloud"`!

## Langkah 3.5 — Aktifkan Jadwal Kerja Otomatis (`/automation`)
Supaya tim bekerja otomatis setiap hari tanpa perlu Anda chat atau menyalakan komputer:

1. Di kotak chat Remote Project, ketik:
   ```text
   /automation
   ```
2. Ikuti panduan singkat yang muncul di layar:
   - **Jadwal (Cadence):** `Daily` (Harian), misalnya pukul **`08:00 WIB` (`Asia/Jakarta`)**.
   - **Instruksi Otomasi:**
     ```text
     1. Cek perintah/chat Bos Ardy dulu lewat `python3 scripts/office_bridge.py --check-command`. Jika ada perintah pending, eksekusi dulu lalu jalankan `--ack-command`.
     2. Jalankan estafet konten harian niche [ISI NICHE ANDA] menggunakan skill sentod-analis, jubaidah-editor, dan bodat-uploader sesuai AGENTS.md.
     3. Selalu update pergerakan agen ke Kantor 3D menggunakan scripts/office_bridge.py, lalu berhenti di tahap ACC Bos Ardy dan kirim laporan ringkas ke saya.
     ```
   - Saat ditanya **"Execute a test run now to configure permissions?"**, pilih **Yes** agar semua izin terekam otomatis.
3. Buka tab **Automations** dan pastikan tombol **Enable** sudah menyala.

*(Opsional)* Jika Anda juga ingin tim AI rajin mengecek pesan chat yang Anda ketik dari Kantor 3D sepanjang hari, Anda bisa membuat 1 automasi ringan tambahan tiap **15–30 menit**:
> *"Jalankan `python3 scripts/office_bridge.py --check-command`. Jika statusnya `pending`, jalankan perintah Bos Ardy tersebut (misal ACC upload, revisi, atau pindah ruangan), update status Kantor 3D, lalu jalankan `--ack-command`. Jika tidak ada perintah `pending`, langsung selesai tanpa melakukan apa pun."*

---

# BAGIAN 4: Troubleshooting Cepat (Jika Ada Kendala)

| Gejala / Masalah | Penyebab Utama | Cara Memperbaiki |
| :--- | :--- | :--- |
| **Kantor 3D tampil polos / teks kode mentah** | Saat menyalin `index.html` ke `Index.html` ikut menyalin baris ` ```html ` di atas atau ` ``` ` di bawah. | Buka `Index.html` di Apps Script, hapus baris ` ```html ` di paling atas dan ` ``` ` di paling bawah, simpan, lalu **Deploy -> Manage deployments -> Edit -> New version -> Deploy**. |
| **Karakter di Kantor 3D tidak bergerak saat tes `--test`** | `GAS_OFFICE_TOKEN` di Antigravity berbeda dengan `SECRET_TOKEN` di `Code.gs`, atau akses Web App belum `Anyone`. | Samakan token di kedua tempat, pastikan **Who has access: Anyone**, lalu buat **New version** saat deploy ulang. |
| **Muncul peringatan *"Google hasn't verified this app"*** | Skrip Apps Script adalah proyek pribadi Anda sendiri. | Klik **Advanced** -> **Go to Ardy-AI-Office-3D (unsafe)** -> **Allow**. |
| **Edit `Code.gs` atau `Index.html` tapi tampilan di HP belum berubah** | Apps Script masih menjalankan versi deployment lama. | Klik **Deploy -> Manage deployments -> klik ikon Pensil -> pilih `New version` -> Deploy**. |
| **Antigravity error `No module named 'requests'`** | Library Python `requests` belum diinstall di sandbox. | Minta Antigravity menjalankan `pip install requests` di chat. |
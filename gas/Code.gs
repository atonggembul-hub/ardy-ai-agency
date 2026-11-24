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

// =========================================================================
// ARDY AI AGENCY HQ — GOOGLE APPS SCRIPT BRIDGE & 3D OFFICE HOST (v2 AI CHAT)
// =========================================================================

// WAJIB GANTI dengan kata sandi rahasia Anda sendiri (samakan dengan GAS_OFFICE_TOKEN di Antigravity)
// Tips: Anda juga bisa menyimpannya di Project Settings -> Script Properties dengan key SECRET_TOKEN
const SECRET_TOKEN = 'ARDY_HQ_2026_RAHASIA';

const STATE_KEY = 'ARDY_OFFICE_STATE_JSON';
const COMMAND_KEY = 'ARDY_BOSS_COMMAND_JSON';
const CHATS_KEY = 'ARDY_AGENT_CHATS_JSON';
const INBOX_KEY = 'ARDY_CHAT_INBOX_JSON';
const MAX_CHAT_HISTORY = 25;

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

function getEffectiveToken() {
  const propToken = PropertiesService.getScriptProperties().getProperty('SECRET_TOKEN');
  return (propToken && propToken.trim()) ? propToken.trim() : SECRET_TOKEN;
}

function getTimeWIB() {
  return Utilities.formatDate(new Date(), 'Asia/Jakarta', 'HH:mm');
}

function loadJsonProp(props, key, fallback) {
  const raw = props.getProperty(key);
  if (!raw) return JSON.parse(JSON.stringify(fallback));
  try {
    return JSON.parse(raw);
  } catch (_) {
    return JSON.parse(JSON.stringify(fallback));
  }
}

function getFullOfficeBundle() {
  const props = PropertiesService.getScriptProperties();
  const state = loadJsonProp(props, STATE_KEY, DEFAULT_STATE);
  const chats = loadJsonProp(props, CHATS_KEY, { ardy: [], sentod: [], jubaidah: [], bodat: [] });
  const inbox = loadJsonProp(props, INBOX_KEY, []);

  // Gabungkan chat dari CHATS_KEY (jika ada) dengan state.chats (kompatibilitas v1)
  const mergedChats = state.chats || {};
  ['ardy', 'sentod', 'jubaidah', 'bodat'].forEach(function(k) {
    if (Array.isArray(chats[k]) && chats[k].length > 0) {
      mergedChats[k] = chats[k];
    } else if (!Array.isArray(mergedChats[k])) {
      mergedChats[k] = [];
    }
  });

  const pendingAgents = [];
  inbox.forEach(function(item) {
    if (item && item.status === 'pending' && item.agent && pendingAgents.indexOf(item.agent) === -1) {
      pendingAgents.push(item.agent);
    }
  });

  state.chats = mergedChats;
  state.pending_agents = pendingAgents;
  return state;
}

/**
 * Menangani tampilan Kantor 3D di browser & permintaan GET API dari Antigravity
 */
function doGet(e) {
  const params = (e && e.parameter) ? e.parameter : {};
  const api = params.api || '';
  const validToken = getEffectiveToken();

  // 1. Cek status JSON terbaru + riwayat chat agen (?api=state)
  if (api === 'state') {
    return jsonResponse(getFullOfficeBundle());
  }

  // 2. Antigravity mengambil antrean pesan chat per karakter (?api=inbox&token=...)
  if (api === 'inbox') {
    if ((params.token || '') !== validToken) {
      return jsonResponse({ ok: false, error: 'Token tidak valid' });
    }
    const props = PropertiesService.getScriptProperties();
    const inbox = loadJsonProp(props, INBOX_KEY, []);
    const pending = inbox.filter(function(item) { return item && item.status === 'pending'; });

    // Kompatibilitas dengan COMMAND_KEY lama jika ada pending yang belum masuk inbox
    const legacyCmd = loadJsonProp(props, COMMAND_KEY, { command: null, status: 'none' });
    if (legacyCmd && legacyCmd.status === 'pending' && legacyCmd.command) {
      const alreadyQueued = pending.some(function(p) { return p.raw_command === legacyCmd.command || p.text === legacyCmd.command; });
      if (!alreadyQueued) {
        pending.push({
          id: 'legacy_' + (legacyCmd.created_at || 'cmd'),
          agent: inferAgentFromText(legacyCmd.command),
          text: legacyCmd.command,
          created_at: legacyCmd.created_at || new Date().toISOString(),
          status: 'pending'
        });
      }
    }

    const bundle = getFullOfficeBundle();
    return jsonResponse({
      ok: true,
      pending: pending,
      chats: bundle.chats,
      state: bundle
    });
  }

  // 3. Endpoint lama (?api=command&token=...) tetap didukung penuh
  if (api === 'command') {
    if ((params.token || '') !== validToken) {
      return jsonResponse({ ok: false, error: 'Token tidak valid' });
    }
    const props = PropertiesService.getScriptProperties();
    const inbox = loadJsonProp(props, INBOX_KEY, []);
    const firstPending = inbox.filter(function(i) { return i && i.status === 'pending'; })[0];
    if (firstPending) {
      return jsonResponse({
        id: firstPending.id,
        agent: firstPending.agent,
        command: firstPending.text,
        created_at: firstPending.created_at,
        status: 'pending'
      });
    }
    const raw = props.getProperty(COMMAND_KEY) || JSON.stringify({ command: null, status: 'none' });
    return ContentService.createTextOutput(raw).setMimeType(ContentService.MimeType.JSON);
  }

  // 4. Default: Tampilkan aplikasi Kantor AI Agent 3D (Index.html)
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Kantor AI Agent 3D — Ardy HQ')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
}

/**
 * Menerima balasan AI Agent, chat Bos Ardy (dari GitHub Pages dengan token), atau update status Kantor 3D
 */
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ ok: false, error: 'Body JSON kosong' });
    }

    const payload = JSON.parse(e.postData.contents);
    if (payload.token !== getEffectiveToken()) {
      return jsonResponse({ ok: false, error: 'Unauthorized: token tidak cocok' });
    }

    const props = PropertiesService.getScriptProperties();

    // A. Bos Ardy mengirim chat ke karakter dari luar Apps Script (mis. GitHub Pages + Token)
    if (payload.action === 'user_chat') {
      const saved = recordUserChatInternal(props, payload.agent || 'ardy', payload.text || '', payload.id);
      return jsonResponse({ ok: true, saved: saved });
    }

    // B. AI Agent di Antigravity mengirim balasan cerdas ke karakter tertentu
    if (payload.action === 'agent_reply') {
      const agentKey = ['ardy', 'sentod', 'jubaidah', 'bodat'].indexOf(payload.agent) !== -1 ? payload.agent : 'ardy';
      const chats = loadJsonProp(props, CHATS_KEY, { ardy: [], sentod: [], jubaidah: [], bodat: [] });
      if (!Array.isArray(chats[agentKey])) chats[agentKey] = [];

      // Pastikan pesan user masuk riwayat bila dikirim lewat jalur legacy
      if (payload.user_text) {
        const existsUser = chats[agentKey].some(function(m) {
          return m.sender === 'user' && (m.id === payload.id || m.text === payload.user_text);
        });
        if (!existsUser) {
          chats[agentKey].push({
            id: payload.id || ('usr_' + Date.now()),
            sender: 'user',
            text: String(payload.user_text),
            time: getTimeWIB(),
            created_at: new Date().toISOString()
          });
        }
      }

      const replyMsg = {
        id: 'rep_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
        reply_to: payload.id || null,
        sender: 'agent',
        text: String(payload.reply || ''),
        bubble: String(payload.bubble || ''),
        time: getTimeWIB(),
        created_at: new Date().toISOString()
      };
      chats[agentKey].push(replyMsg);
      if (chats[agentKey].length > MAX_CHAT_HISTORY) {
        chats[agentKey] = chats[agentKey].slice(-MAX_CHAT_HISTORY);
      }
      props.setProperty(CHATS_KEY, JSON.stringify(chats));

      // Tandai pesan inbox selesai
      const inbox = loadJsonProp(props, INBOX_KEY, []);
      const updatedInbox = inbox.map(function(item) {
        if (!item) return item;
        if ((payload.id && item.id === payload.id) || (!payload.id && item.agent === agentKey && item.status === 'pending')) {
          item.status = 'done';
          item.done_at = new Date().toISOString();
        }
        return item;
      }).filter(function(item, idx, arr) {
        return item && (item.status === 'pending' || idx >= arr.length - 12);
      });
      props.setProperty(INBOX_KEY, JSON.stringify(updatedInbox));

      // Tandai COMMAND_KEY legacy selesai juga
      const currentRaw = props.getProperty(COMMAND_KEY);
      if (currentRaw) {
        try {
          const currentCmd = JSON.parse(currentRaw);
          if (currentCmd.status === 'pending') {
            currentCmd.status = 'done';
            currentCmd.done_at = new Date().toISOString();
            props.setProperty(COMMAND_KEY, JSON.stringify(currentCmd));
          }
        } catch (_) {}
      }

      // Update juga state ruangan/status/bubble agen jika disertakan
      const state = loadJsonProp(props, STATE_KEY, DEFAULT_STATE);
      if (!state.agents) state.agents = {};
      if (!state.agents[agentKey]) state.agents[agentKey] = { status: 'Aktif', room: 'workspace', task: '' };
      if (payload.room) state.agents[agentKey].room = payload.room;
      if (payload.status) state.agents[agentKey].status = payload.status;
      if (payload.task !== undefined && payload.task !== null) state.agents[agentKey].task = payload.task;
      if (payload.bubble) {
        state.agents[agentKey].bubble = payload.bubble;
        state.agents[agentKey].bubble_id = replyMsg.id;
      }
      if (payload.mode) state.mode = payload.mode;
      if (payload.approval_needed !== undefined && payload.approval_needed !== null) {
        state.approval_needed = Boolean(payload.approval_needed);
      }
      if (payload.approval_message !== undefined && payload.approval_message !== null) {
        state.approval_message = String(payload.approval_message);
      }
      state.chats = chats;
      state.updated_at = new Date().toISOString();
      props.setProperty(STATE_KEY, JSON.stringify(state));

      return jsonResponse({ ok: true, message: 'Balasan AI Agent tersimpan', reply: replyMsg });
    }

    // C. Konfirmasi selesai perintah (ack_command)
    if (payload.action === 'ack_command') {
      const currentRaw = props.getProperty(COMMAND_KEY);
      if (currentRaw) {
        const currentCmd = JSON.parse(currentRaw);
        currentCmd.status = 'done';
        currentCmd.done_at = new Date().toISOString();
        props.setProperty(COMMAND_KEY, JSON.stringify(currentCmd));
      }
      const inbox = loadJsonProp(props, INBOX_KEY, []);
      inbox.forEach(function(item) {
        if (item && item.status === 'pending' && (!payload.id || item.id === payload.id)) {
          item.status = 'done';
          item.done_at = new Date().toISOString();
        }
      });
      props.setProperty(INBOX_KEY, JSON.stringify(inbox.slice(-15)));
      return jsonResponse({ ok: true, message: 'Perintah Bos Ardy ditandai selesai (done)' });
    }

    // D. Default: Simpan update status Kantor 3D (pertahankan CHATS_KEY yang sudah ada bila lebih lengkap)
    delete payload.token;
    const existingChats = loadJsonProp(props, CHATS_KEY, { ardy: [], sentod: [], jubaidah: [], bodat: [] });
    if (payload.chats && typeof payload.chats === 'object') {
      ['ardy', 'sentod', 'jubaidah', 'bodat'].forEach(function(k) {
        if (Array.isArray(payload.chats[k]) && payload.chats[k].length >= (existingChats[k] || []).length) {
          existingChats[k] = payload.chats[k].slice(-MAX_CHAT_HISTORY);
        }
      });
      props.setProperty(CHATS_KEY, JSON.stringify(existingChats));
    }
    payload.chats = existingChats;
    payload.updated_at = new Date().toISOString();
    props.setProperty(STATE_KEY, JSON.stringify(payload));

    return jsonResponse({
      ok: true,
      message: 'Status Kantor 3D berhasil diperbarui',
      updated_at: payload.updated_at
    });
  } catch (err) {
    return jsonResponse({ ok: false, error: err.message });
  } finally {
    lock.releaseLock();
  }
}

function inferAgentFromText(raw) {
  const s = String(raw || '').toLowerCase();
  if (s.indexOf('[chat:sentod') === 0 || s.indexOf('untuk sentod') !== -1) return 'sentod';
  if (s.indexOf('[chat:jubaidah') === 0 || s.indexOf('untuk jubaidah') !== -1) return 'jubaidah';
  if (s.indexOf('[chat:bodat') === 0 || s.indexOf('untuk bodat') !== -1) return 'bodat';
  return 'ardy';
}

function recordUserChatInternal(props, agentKey, messageText, customId) {
  const key = ['ardy', 'sentod', 'jubaidah', 'bodat'].indexOf(agentKey) !== -1 ? agentKey : 'ardy';
  const cleanText = String(messageText || '').trim();
  const msgId = customId || ('msg_' + Date.now() + '_' + Math.floor(Math.random() * 1000));
  const nowIso = new Date().toISOString();

  const chats = loadJsonProp(props, CHATS_KEY, { ardy: [], sentod: [], jubaidah: [], bodat: [] });
  if (!Array.isArray(chats[key])) chats[key] = [];
  chats[key].push({
    id: msgId,
    sender: 'user',
    text: cleanText,
    time: getTimeWIB(),
    created_at: nowIso
  });
  if (chats[key].length > MAX_CHAT_HISTORY) {
    chats[key] = chats[key].slice(-MAX_CHAT_HISTORY);
  }
  props.setProperty(CHATS_KEY, JSON.stringify(chats));

  const inbox = loadJsonProp(props, INBOX_KEY, []);
  inbox.push({
    id: msgId,
    agent: key,
    text: cleanText,
    created_at: nowIso,
    status: 'pending'
  });
  props.setProperty(INBOX_KEY, JSON.stringify(inbox.slice(-20)));

  // Mirror ke COMMAND_KEY agar --check-command tetap terbaca
  props.setProperty(COMMAND_KEY, JSON.stringify({
    id: msgId,
    agent: key,
    command: '[CHAT:' + key + ':' + msgId + '] ' + cleanText,
    created_at: nowIso,
    status: 'pending'
  }));

  return { id: msgId, agent: key, text: cleanText, created_at: nowIso };
}

/**
 * Dipanggil otomatis oleh Index.html setiap 2.5–5 detik
 */
function getOfficeState() {
  return getFullOfficeBundle();
}

/**
 * Dipanggil oleh Index.html saat Bos Ardy men-chat salah satu karakter (Sentod/Jubaidah/Bodat/Ardy)
 */
function sendAgentChat(agentKey, messageText, customId) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const props = PropertiesService.getScriptProperties();
    const saved = recordUserChatInternal(props, agentKey, messageText, customId);
    return { ok: true, saved: saved };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Menghapus riwayat chat satu karakter dari Index.html
 */
function clearAgentChat(agentKey) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const key = ['ardy', 'sentod', 'jubaidah', 'bodat'].indexOf(agentKey) !== -1 ? agentKey : 'ardy';
    const props = PropertiesService.getScriptProperties();
    const chats = loadJsonProp(props, CHATS_KEY, { ardy: [], sentod: [], jubaidah: [], bodat: [] });
    chats[key] = [];
    props.setProperty(CHATS_KEY, JSON.stringify(chats));
    return { ok: true };
  } finally {
    lock.releaseLock();
  }
}

/**
 * Dipanggil saat Bos Ardy klik tombol komando umum / "Kirim ACC Langsung"
 */
function sendBossCommand(commandText) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const props = PropertiesService.getScriptProperties();
    const raw = String(commandText || '').trim();
    const agent = inferAgentFromText(raw);
    const cleaned = raw.replace(/^\[CHAT:[a-z]+:[^\]]+\]\s*/i, '');
    const saved = recordUserChatInternal(props, agent, cleaned, null);
    return { ok: true, saved: saved };
  } finally {
    lock.releaseLock();
  }
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

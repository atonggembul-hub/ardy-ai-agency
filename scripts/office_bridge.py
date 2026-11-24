#!/usr/bin/env python3
"""
Jembatan 2 Arah Google Antigravity Remote <-> Kantor 3D Google Apps Script (v2 Multi-Agent Brain).
Menggunakan Environment Variables:
  - GAS_OFFICE_URL   : Web App URL Apps Script (/exec)
  - GAS_OFFICE_TOKEN : SECRET_TOKEN yang sama persis dengan di Code.gs

Mendukung:
  - --check-command / --inbox : Cek pesan/chat terbaru dari Bos Ardy per karakter
  - --watch-once              : Listener reaktif (bangunkan Antigravity otomatis begitu ada chat masuk)
  - --reply                   : Kirim balasan cerdas AI Agent spesifik karakter + balon 3D + gerak ruangan
  - --ack-command             : Tandai perintah selesai
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

WIB = timezone(timedelta(hours=7))
REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_STATE_FILE = REPO_ROOT / "office_state.json"
LOCAL_CHATS_FILE = REPO_ROOT / "logs" / "agent_chats.json"
MAX_CHAT_HISTORY = 25

GAS_URL = os.environ.get("GAS_OFFICE_URL", "").strip()
GAS_TOKEN = os.environ.get("GAS_OFFICE_TOKEN", "").strip()

DEFAULT_STATE = {
    "mode": "work",
    "approval_needed": False,
    "approval_message": "",
    "agents": {
        "ardy":     {"status": "Mengawasi",     "room": "boss",      "task": "Memantau cloud Antigravity"},
        "sentod":   {"status": "Standby",       "room": "workspace", "task": "Siap riset tren"},
        "jubaidah": {"status": "Standby",       "room": "workspace", "task": "Siap edit video"},
        "bodat":    {"status": "Standby",       "room": "workspace", "task": "Siap tulis caption"},
    },
}

AGENT_PERSONAS = {
    "ardy": {
        "name": "Bos Ardy (Co-Pilot Komando Ruang Bos)",
        "role": "Chief Strategy & Operations AI",
        "style": (
            "Taktis, ringkas, berwibawa namun santai selayaknya Co-CEO/Kepala Operasional kreatif. "
            "Fokus pada koordinasi lintas tim (Sentod, Jubaidah, Bodat), KPI views, efisiensi produksi, "
            "dan pengambilan keputusan strategis."
        ),
        "expertise": (
            "Mengecek status riil seluruh folder produksi (00_raw_assets, 01_briefs, 02_edited_videos, "
            "03_ready_to_post), mengatur mode kantor (work/meeting/coffee), membagi tugas ke agen lain, "
            "dan merangkum laporan eksekutif."
        ),
    },
    "sentod": {
        "name": "Sentod",
        "role": "Analis Konten & Riset Tren",
        "style": (
            "Tajam, kritis, antusias soal algoritma short-form & psikologi penonton. Suka memakai istilah "
            "kreator secara natural (hook 3 detik, curiosity gap, retention drop, pattern interrupt). "
            "Selalu menyapa 'Bos Ardy' dan berani memberi saran sudut pandang yang lebih nendang."
        ),
        "expertise": (
            "Riset tren viral real-time via Google Search, bedah kompetitor, merancang hook 3 detik yang "
            "menghentikan scroll, menyusun skrip padat retensi, dan menulis brief ke 01_briefs/."
        ),
    },
    "jubaidah": {
        "name": "Jubaidah",
        "role": "Senior Video Editor 9:16 & QA Teknis",
        "style": (
            "Cekatan, perfeksionis soal visual & kualitas audio, ekspresif dan ramah ('Siap Bos Ardy!', "
            "'Jangan sampai visualnya flat Bos!'). Sangat peduli pacing cepat, beat cut, keterbacaan subtitle, "
            "dan kualitas render."
        ),
        "expertise": (
            "Editing vertikal 9:16 (1080x1920, 30fps), FFmpeg & Remotion kinetic typography, face tracking, "
            "sound design (whoosh/pop/boom), normalisasi audio -16 LUFS, serta QA ffprobe di 02_edited_videos/."
        ),
    },
    "bodat": {
        "name": "Bodat",
        "role": "Copywriter, Spesialis SEO & Uploader",
        "style": (
            "Kreatif, luwes/gaul, jago storytelling dan memancing diskusi/komentar netizen di kolom komentar, "
            "paham jam prime time posting, serta sangat disiplin menjaga aturan: pantang upload live sebelum "
            "ada ACC eksplisit dari Bos Ardy."
        ),
        "expertise": (
            "Menulis 3 variasi caption (Santai, Edukatif, Pancing Komentar), riset hashtag SEO TikTok/Reels/Shorts, "
            "membundel paket di 03_ready_to_post/, dan memproses publikasi/arsip pasca ACC Bos Ardy."
        ),
    },
}


def now_wib_hhmm() -> str:
    return datetime.now(WIB).strftime("%H:%M")


def now_iso() -> str:
    return datetime.now(WIB).isoformat(timespec="seconds")


def check_env() -> None:
    if not GAS_URL or not GAS_TOKEN:
        print(
            "ERROR: GAS_OFFICE_URL atau GAS_OFFICE_TOKEN belum diset di Environment Variables!",
            file=sys.stderr,
        )
        sys.exit(1)


def load_local_state() -> dict:
    if LOCAL_STATE_FILE.exists():
        try:
            data = json.loads(LOCAL_STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("agents", {})
                for k, v in DEFAULT_STATE["agents"].items():
                    data["agents"].setdefault(k, dict(v))
                return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def save_local_state(state: dict) -> None:
    state["updated_at"] = now_iso()
    LOCAL_STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_local_chats() -> dict:
    base = {"ardy": [], "sentod": [], "jubaidah": [], "bodat": []}
    if LOCAL_CHATS_FILE.exists():
        try:
            loaded = json.loads(LOCAL_CHATS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for k in base:
                    if isinstance(loaded.get(k), list):
                        base[k] = loaded[k][-MAX_CHAT_HISTORY:]
        except Exception:
            pass
    return base


def save_local_chats(chats: dict) -> None:
    LOCAL_CHATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    cleaned = {
        k: (chats.get(k, [])[-MAX_CHAT_HISTORY:] if isinstance(chats.get(k), list) else [])
        for k in ("ardy", "sentod", "jubaidah", "bodat")
    }
    LOCAL_CHATS_FILE.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_legacy_command_string(raw_cmd: str) -> tuple[str, str, str | None]:
    """Ekstrak (agent_key, clean_user_text, msg_id) dari format string baru maupun legacy."""
    text = (raw_cmd or "").strip()
    m = re.match(r"^\[CHAT:(ardy|sentod|jubaidah|bodat):([^\]]+)\]\s*(.*)$", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).lower(), m.group(3).strip(), m.group(2).strip()

    prefixes = [
        ("ardy", "Instruksi Bos Ardy untuk seluruh tim (Sentod, Jubaidah, Bodat):"),
        ("sentod", "Perintah Bos Ardy untuk Sentod (Analis Konten):"),
        ("jubaidah", "Perintah Bos Ardy untuk Jubaidah (Editing Video):"),
        ("bodat", "Perintah Bos Ardy untuk Bodat (Caption & Uploader):"),
    ]
    lower = text.lower()
    for ag, pref in prefixes:
        if lower.startswith(pref.lower()):
            return ag, text[len(pref):].strip(), None

    if "untuk sentod" in lower:
        return "sentod", text, None
    if "untuk jubaidah" in lower:
        return "jubaidah", text, None
    if "untuk bodat" in lower:
        return "bodat", text, None
    return "ardy", text, None


def fetch_inbox() -> dict:
    """Ambil pesan pending dari Code.gs v2 (?api=inbox) dengan fallback mulus ke Code.gs v1 (?api=command)."""
    check_env()
    # Coba endpoint v2 (?api=inbox)
    resp = requests.get(
        GAS_URL,
        params={"api": "inbox", "token": GAS_TOKEN},
        timeout=20,
        allow_redirects=True,
    )
    resp.raise_for_status()
    body = resp.text.strip()
    if body.startswith("{"):
        try:
            data = json.loads(body)
            if data.get("ok") and "pending" in data:
                # Rapikan tiap item pending
                normalized = []
                for item in data.get("pending", []):
                    ag, clean_txt, parsed_id = parse_legacy_command_string(item.get("text", ""))
                    agent_key = item.get("agent") if item.get("agent") in AGENT_PERSONAS else ag
                    normalized.append(
                        {
                            "id": item.get("id") or parsed_id or f"msg_{int(time.time())}",
                            "agent": agent_key,
                            "text": clean_txt or item.get("text", ""),
                            "created_at": item.get("created_at", ""),
                            "status": "pending",
                        }
                    )
                data["pending"] = normalized
                return data
        except json.JSONDecodeError:
            pass

    # Fallback otomatis ke Code.gs v1 (?api=command)
    resp_cmd = requests.get(
        GAS_URL,
        params={"api": "command", "token": GAS_TOKEN},
        timeout=20,
        allow_redirects=True,
    )
    resp_cmd.raise_for_status()
    cmd_data = json.loads(resp_cmd.text)
    pending = []
    if cmd_data.get("status") == "pending" and cmd_data.get("command"):
        ag, clean_txt, parsed_id = parse_legacy_command_string(cmd_data["command"])
        agent_key = cmd_data.get("agent") if cmd_data.get("agent") in AGENT_PERSONAS else ag
        msg_id = cmd_data.get("id") or parsed_id or f"legacy_{cmd_data.get('created_at', int(time.time()))}"
        pending.append(
            {
                "id": msg_id,
                "agent": agent_key,
                "text": clean_txt,
                "raw_command": cmd_data["command"],
                "created_at": cmd_data.get("created_at", ""),
                "status": "pending",
            }
        )
    return {"ok": True, "pending": pending, "chats": load_local_chats(), "v1_fallback": True}


def push_state(state: dict, git_push: bool = False, commit_msg: str | None = None) -> None:
    check_env()
    chats = load_local_chats()
    if "chats" not in state or not isinstance(state["chats"], dict):
        state["chats"] = chats
    save_local_state(state)

    payload = dict(state)
    payload["token"] = GAS_TOKEN
    resp = requests.post(GAS_URL, json=payload, timeout=25, allow_redirects=True)
    resp.raise_for_status()
    print("PUSH OK:", resp.text)

    if git_push:
        git_sync_state(commit_msg or f"chore(office): sync office_state ({state.get('mode', 'work')})")


def git_sync_state(commit_msg: str) -> None:
    try:
        subprocess.run(["git", "add", "office_state.json"], cwd=REPO_ROOT, check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_ROOT)
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
            subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True)
            print(f"GIT PUSH OK: {commit_msg}")
    except subprocess.CalledProcessError as exc:
        print(f"WARN: git push gagal: {exc}", file=sys.stderr)


def ack_boss_command(msg_id: str | None = None) -> None:
    check_env()
    payload = {"token": GAS_TOKEN, "action": "ack_command"}
    if msg_id:
        payload["id"] = msg_id
    resp = requests.post(GAS_URL, json=payload, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    print("ACK OK:", resp.text)


def send_agent_reply(
    agent: str,
    reply_text: str,
    bubble_text: str | None = None,
    user_text: str | None = None,
    msg_id: str | None = None,
    room: str | None = None,
    status: str | None = None,
    task: str | None = None,
    mode: str | None = None,
    approval_needed: bool | None = None,
    approval_message: str | None = None,
    git_push: bool = False,
) -> None:
    check_env()
    chats = load_local_chats()
    ag_chats = chats.setdefault(agent, [])

    if user_text:
        already = any(
            m.get("sender") == "user" and (
                (msg_id and m.get("id") == msg_id) or m.get("text") == user_text
            )
            for m in ag_chats[-5:]
        )
        if not already:
            ag_chats.append(
                {
                    "id": msg_id or f"usr_{int(time.time() * 1000)}",
                    "sender": "user",
                    "text": user_text,
                    "time": now_wib_hhmm(),
                    "created_at": now_iso(),
                }
            )

    short_bubble = (bubble_text or "").strip()
    if not short_bubble:
        first_line = reply_text.strip().splitlines()[0] if reply_text.strip() else "Siap Bos Ardy!"
        short_bubble = (first_line[:54] + "…") if len(first_line) > 55 else first_line

    rep_entry = {
        "id": f"rep_{int(time.time() * 1000)}",
        "reply_to": msg_id,
        "sender": "agent",
        "text": reply_text.strip(),
        "bubble": short_bubble,
        "time": now_wib_hhmm(),
        "created_at": now_iso(),
    }
    ag_chats.append(rep_entry)
    chats[agent] = ag_chats[-MAX_CHAT_HISTORY:]
    save_local_chats(chats)

    # Update local state juga
    state = load_local_state()
    ag_state = state["agents"].setdefault(agent, {"status": "Aktif", "room": "workspace", "task": ""})
    if room:
        ag_state["room"] = room
    if status:
        ag_state["status"] = status
    if task is not None:
        ag_state["task"] = task
    ag_state["bubble"] = short_bubble
    ag_state["bubble_id"] = rep_entry["id"]

    if mode:
        state["mode"] = mode
    if approval_needed is not None:
        state["approval_needed"] = approval_needed
    if approval_message is not None:
        state["approval_message"] = approval_message
    state["chats"] = chats
    save_local_state(state)

    # Coba endpoint v2 action="agent_reply"
    payload = {
        "token": GAS_TOKEN,
        "action": "agent_reply",
        "id": msg_id,
        "agent": agent,
        "user_text": user_text,
        "reply": reply_text.strip(),
        "bubble": short_bubble,
        "room": room,
        "status": status,
        "task": task,
        "mode": mode,
        "approval_needed": approval_needed,
        "approval_message": approval_message,
    }
    resp = requests.post(GAS_URL, json=payload, timeout=25, allow_redirects=True)
    resp.raise_for_status()

    handled_by_v2 = False
    try:
        rj = resp.json()
        if rj.get("ok") and "Balasan AI Agent" in rj.get("message", ""):
            handled_by_v2 = True
            print("REPLY V2 OK:", resp.text)
    except Exception:
        pass

    # Jika Code.gs di cloud masih versi v1, push_state penuh + ack_command tetap menyimpan chats & bubble!
    if not handled_by_v2:
        push_payload = dict(state)
        push_payload["token"] = GAS_TOKEN
        r_push = requests.post(GAS_URL, json=push_payload, timeout=25, allow_redirects=True)
        r_push.raise_for_status()
        ack_boss_command(msg_id)
        print("REPLY V1-COMPAT OK:", r_push.text)

    if git_push:
        git_sync_state(f"chore(chat): {agent} membalas chat Bos Ardy")


def watch_once(poll_interval: float = 2.5, max_seconds: int = 3600) -> None:
    """Pantau pesan masuk dari Kantor 3D; keluar (exit 0) begitu ada chat pending agar Antigravity bangun."""
    check_env()
    start = time.time()
    while time.time() - start < max_seconds:
        try:
            inbox = fetch_inbox()
            pending = inbox.get("pending", [])
            if pending:
                # Sinkronkan riwayat chat dari server bila lebih baru
                srv_chats = inbox.get("chats")
                if isinstance(srv_chats, dict):
                    local_chats = load_local_chats()
                    for k in ("ardy", "sentod", "jubaidah", "bodat"):
                        if isinstance(srv_chats.get(k), list) and len(srv_chats[k]) >= len(local_chats.get(k, [])):
                            local_chats[k] = srv_chats[k]
                    save_local_chats(local_chats)

                first = pending[0]
                ag_key = first["agent"]
                persona = AGENT_PERSONAS.get(ag_key, AGENT_PERSONAS["ardy"])

                # Beri indikator instan di Kantor 3D bahwa karakter sedang berpikir
                try:
                    st = load_local_state()
                    st.setdefault("agents", {}).setdefault(ag_key, {})
                    st["agents"][ag_key]["status"] = "Sedang Mikir💭"
                    st["agents"][ag_key]["task"] = f"Memikirkan jawaban untuk: {first['text'][:60]}"
                    st["agents"][ag_key]["bubble"] = "💭 Sedang memikirkan jawaban..."
                    st["chats"] = load_local_chats()
                    p = dict(st)
                    p["token"] = GAS_TOKEN
                    requests.post(GAS_URL, json=p, timeout=12, allow_redirects=True)
                except Exception:
                    pass

                history = load_local_chats().get(ag_key, [])[-8:]
                report = {
                    "event": "NEW_AGENT_CHAT",
                    "pending_count": len(pending),
                    "all_pending": pending,
                    "target_agent": ag_key,
                    "persona": persona,
                    "message_id": first["id"],
                    "user_message": first["text"],
                    "recent_history": history,
                }
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return
        except Exception as exc:
            print(f"[watch_once] transient error: {exc}", file=sys.stderr)
        time.sleep(poll_interval)

    print(json.dumps({"event": "WATCH_TIMEOUT", "pending_count": 0}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Bridge 2-Arah Kantor 3D Ardy HQ (Multi-Agent AI)")
    parser.add_argument("--test", action="store_true", help="Kirim status uji coba ke Kantor 3D")
    parser.add_argument("--check-command", action="store_true", help="Cek chat/perintah terbaru dari Bos Ardy")
    parser.add_argument("--inbox", action="store_true", help="Tampilkan antrean lengkap chat per karakter")
    parser.add_argument("--watch-once", action="store_true", help="Tunggu sampai ada chat baru lalu bangunkan AI")
    parser.add_argument("--watch-timeout", type=int, default=3600, help="Batas detik --watch-once (default: 3600)")
    parser.add_argument("--ack-command", action="store_true", help="Tandai perintah Bos Ardy sudah selesai")
    parser.add_argument("--personas", action="store_true", help="Cetak profil kecerdasan 4 karakter")

    parser.add_argument("--reply", action="store_true", help="Kirim balasan chat sebagai karakter AI")
    parser.add_argument("--message", type=str, help="Isi balasan lengkap karakter AI (untuk --reply)")
    parser.add_argument("--bubble", type=str, help="Teks singkat balon bicara 3D di atas kepala karakter")
    parser.add_argument("--user-text", type=str, help="Pesan asli Bos Ardy (untuk kelengkapan log v1)")
    parser.add_argument("--id", type=str, help="ID pesan yang dibalas / di-ack")

    parser.add_argument("--agent", choices=["ardy", "sentod", "jubaidah", "bodat"], help="Agen target")
    parser.add_argument("--room", choices=["boss", "workspace", "meeting", "coffee"], help="Ruangan agen")
    parser.add_argument("--status", type=str, help="Label status singkat (max 15 huruf)")
    parser.add_argument("--task", type=str, help="Deskripsi tugas agen saat ini")
    parser.add_argument("--mode", choices=["work", "meeting", "coffee"], help="Mode global kantor")
    parser.add_argument("--approval-needed", choices=["true", "false"], help="Tampilkan banner ACC Bos Ardy")
    parser.add_argument("--approval-message", type=str, help="Pesan banner ACC Bos Ardy")
    parser.add_argument("--git-push", action="store_true", help="Sekaligus commit & push office_state.json ke GitHub")
    args = parser.parse_args()

    if args.personas:
        print(json.dumps(AGENT_PERSONAS, indent=2, ensure_ascii=False))
        return

    if args.inbox or args.check_command:
        inbox = fetch_inbox()
        print(json.dumps(inbox, indent=2, ensure_ascii=False))
        return

    if args.watch_once:
        watch_once(max_seconds=args.watch_timeout)
        return

    if args.ack_command:
        ack_boss_command(args.id)
        return

    if args.reply:
        if not args.agent or not args.message:
            print("ERROR: --reply wajib menyertakan --agent dan --message", file=sys.stderr)
            sys.exit(1)
        appr = None if args.approval_needed is None else (args.approval_needed == "true")
        send_agent_reply(
            agent=args.agent,
            reply_text=args.message,
            bubble_text=args.bubble,
            user_text=args.user_text,
            msg_id=args.id,
            room=args.room,
            status=args.status,
            task=args.task,
            mode=args.mode,
            approval_needed=appr,
            approval_message=args.approval_message,
            git_push=args.git_push,
        )
        return

    state = load_local_state()

    if args.test:
        state["mode"] = "meeting"
        state["approval_needed"] = False
        for k, st in [
            ("ardy", "Tes Koneksi"),
            ("sentod", "AI Aktif 🧠"),
            ("jubaidah", "AI Aktif 🧠"),
            ("bodat", "AI Aktif 🧠"),
        ]:
            state["agents"][k] = {
                "status": st,
                "room": "meeting",
                "task": "Otak AI Antigravity siap membalas chat!",
            }
        push_state(state, git_push=args.git_push)
        return

    if args.mode:
        state["mode"] = args.mode
    if args.approval_needed is not None:
        state["approval_needed"] = args.approval_needed == "true"
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
        if args.bubble:
            ag["bubble"] = args.bubble
        state["agents"][args.agent] = ag

    push_state(state, git_push=args.git_push)


if __name__ == "__main__":
    main()

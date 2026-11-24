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

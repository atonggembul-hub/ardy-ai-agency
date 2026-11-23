#!/usr/bin/env python3
"""
Helper CLI untuk memperbarui office_state.json di Ardy AI Agency HQ
dan menyinkronkannya ke GitHub agar Kantor AI Agent 3D bergerak real-time.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

VALID_MODES = ("work", "meeting", "coffee")
VALID_ROOMS = ("boss", "workspace", "meeting", "coffee")
VALID_AGENTS = ("ardy", "sentod", "jubaidah", "bodat")

WIB = timezone(timedelta(hours=7))

DEFAULT_STATE = {
    "mode": "work",
    "updated_at": "",
    "approval_needed": False,
    "approval_message": "Kantor AI Agent 3D Ardy HQ aktif dan siap menerima perintah.",
    "agents": {
        "ardy": {"status": "Mengawasi", "room": "boss", "task": "Memantau operasional tim AI"},
        "sentod": {"status": "Siap Riset", "room": "workspace", "task": "Standby riset tren"},
        "jubaidah": {"status": "Siap Edit 9:16", "room": "workspace", "task": "Standby editing video"},
        "bodat": {"status": "Siap Caption", "room": "workspace", "task": "Standby caption & upload"},
    },
}


def find_repo_root(start: Path) -> Path:
    """Cari root repo yang memuat office_state.json atau .git."""
    for candidate in [start, *start.parents]:
        if (candidate / "office_state.json").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd()


def parse_bool(val: str) -> bool:
    lowered = val.strip().lower()
    if lowered in ("true", "1", "yes", "y", "ya"):
        return True
    if lowered in ("false", "0", "no", "n", "tidak"):
        return False
    raise argparse.ArgumentTypeError(f"Nilai boolean tidak valid: {val!r} (gunakan true/false)")


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("agents", {})
                for key, default_agent in DEFAULT_STATE["agents"].items():
                    data["agents"].setdefault(key, dict(default_agent))
                return data
        except json.JSONDecodeError:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def git_push_state(repo_root: Path, state_path: Path, message: str) -> None:
    rel_state = state_path.relative_to(repo_root)
    subprocess.run(["git", "add", str(rel_state)], cwd=repo_root, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
    if diff.returncode == 0:
        print("ℹ️ Tidak ada perubahan baru pada office_state.json; skip commit.")
        return
    subprocess.run(["git", "commit", "-m", message], cwd=repo_root, check=True)
    subprocess.run(["git", "push"], cwd=repo_root, check=True)
    print(f"✅ office_state.json berhasil di-push ke GitHub ({message}).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update office_state.json untuk Kantor AI Agent 3D Ardy HQ")
    parser.add_argument("--state-file", type=Path, default=None, help="Path khusus ke office_state.json")
    parser.add_argument("--mode", choices=VALID_MODES, help="Mode kantor global (work/meeting/coffee)")
    parser.add_argument("--agent", choices=VALID_AGENTS, help="Agen yang statusnya akan diperbarui")
    parser.add_argument("--room", choices=VALID_ROOMS, help="Ruangan tujuan agen")
    parser.add_argument("--status", help="Label status singkat agen (maks ~16 karakter)")
    parser.add_argument("--task", help="Deskripsi tugas agen yang tampil di kartu inspeksi")
    parser.add_argument("--ardy-status", help="Sekaligus update status Bos Ardy")
    parser.add_argument("--ardy-task", help="Sekaligus update tugas Bos Ardy")
    parser.add_argument("--approval-needed", type=parse_bool, default=None, help="Set banner ACC Bos Ardy (true/false)")
    parser.add_argument("--approval-message", help="Pesan notifikasi ACC Bos Ardy")
    parser.add_argument("--set-all-coffee", action="store_true", help="Pindahkan seluruh AI agent ke Area Ngopi")
    parser.add_argument("--set-all-meeting", action="store_true", help="Kumpulkan semua tim ke Ruang Meeting")
    parser.add_argument("--set-all-work", action="store_true", help="Kembalikan semua tim ke mode Kerja")
    parser.add_argument("--push", action="store_true", help="Commit & push office_state.json otomatis ke GitHub")
    parser.add_argument("--commit-message", default=None, help="Pesan commit custom saat menggunakan --push")
    args = parser.parse_args()

    repo_root = find_repo_root(Path(__file__).resolve().parent)
    state_path = args.state_file.resolve() if args.state_file else (repo_root / "office_state.json")
    state = load_state(state_path)

    # Preset global
    if args.set_all_coffee:
        state["mode"] = "coffee"
        state["agents"]["ardy"] = {"status": "Pantau Santai", "room": "boss", "task": "Semua target hari ini selesai"}
        state["agents"]["sentod"] = {"status": "Ngopi Santai", "room": "coffee", "task": "Standby riset konten berikutnya"}
        state["agents"]["jubaidah"] = {"status": "Ngopi Latte", "room": "coffee", "task": "Standby jika ada revisi video"}
        state["agents"]["bodat"] = {"status": "Santai Bistro", "room": "coffee", "task": "Publikasi selesai, istirahat ngopi"}
    elif args.set_all_meeting:
        state["mode"] = "meeting"
        state["agents"]["ardy"] = {"status": "Pimpin Rapat", "room": "meeting", "task": "Memimpin evaluasi strategi konten"}
        state["agents"]["sentod"] = {"status": "Presentasi", "room": "meeting", "task": "Memaparkan insight tren harian"}
        state["agents"]["jubaidah"] = {"status": "Bahas Visual", "room": "meeting", "task": "Menyelaraskan arahan editing 9:16"}
        state["agents"]["bodat"] = {"status": "Catat Strategi", "room": "meeting", "task": "Menyusun jadwal upload & hook caption"}
    elif args.set_all_work:
        state["mode"] = "work"
        state["agents"]["ardy"] = {"status": "Mengawasi", "room": "boss", "task": "Memantau pipeline produksi konten"}
        state["agents"]["sentod"] = {"status": "Riset Tren", "room": "workspace", "task": "Analisis tren viral & brief konten"}
        state["agents"]["jubaidah"] = {"status": "Edit 9:16", "room": "workspace", "task": "Mengolah video & subtitle FFmpeg"}
        state["agents"]["bodat"] = {"status": "Tulis Caption", "room": "workspace", "task": "Menyusun caption & paket upload"}

    if args.mode:
        state["mode"] = args.mode

    if args.agent:
        ag = state["agents"].setdefault(args.agent, {})
        if args.room:
            ag["room"] = args.room
        if args.status is not None:
            ag["status"] = args.status
        if args.task is not None:
            ag["task"] = args.task

    if args.ardy_status is not None:
        state["agents"]["ardy"]["status"] = args.ardy_status
    if args.ardy_task is not None:
        state["agents"]["ardy"]["task"] = args.ardy_task

    if args.approval_needed is not None:
        state["approval_needed"] = args.approval_needed
        if args.approval_needed and args.ardy_status is None:
            state["agents"]["ardy"]["status"] = "Perlu ACC 🔔"
            state["agents"]["ardy"]["room"] = "boss"
            state["agents"]["ardy"]["task"] = "Meninjau paket siap tayang untuk ACC publikasi"

    if args.approval_message is not None:
        state["approval_message"] = args.approval_message

    state["updated_at"] = datetime.now(WIB).isoformat(timespec="seconds")

    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✅ Updated {state_path} (mode={state['mode']}, approval_needed={state['approval_needed']})")

    if args.push:
        commit_msg = args.commit_message
        if not commit_msg:
            if args.agent:
                st = args.status or state["agents"][args.agent].get("status", "update")
                commit_msg = f"chore(office): update {args.agent} -> {st}"
            elif args.set_all_coffee:
                commit_msg = "chore(office): semua tim istirahat ngopi"
            elif args.set_all_meeting:
                commit_msg = "chore(office): semua tim berkumpul di ruang meeting"
            else:
                commit_msg = f"chore(office): update office_state ({state['mode']})"
        try:
            git_push_state(repo_root, state_path, commit_msg)
        except subprocess.CalledProcessError as exc:
            print(f"⚠️ Gagal git push otomatis: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

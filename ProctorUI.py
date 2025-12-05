# ProctorUI.py — ProctorAgent 켜고 끄는 간단 UI (모든 ProctorAgent.exe 강제 종료 버전)

import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import psutil  # 🔥 추가: 프로세스 강제 종료용

# ==== ProctorAgent.exe 위치 찾기 ====
if getattr(sys, "frozen", False):
    # exe로 빌드된 상태
    BASE_DIR = Path(sys.executable).parent
else:
    # python으로 실행할 때
    BASE_DIR = Path(__file__).resolve().parent

AGENT_PATH = BASE_DIR / "ProctorAgent.exe"

proc = None   # UI에서 새로 실행한 프로세스 핸들

def start_agent():
    global proc
    if not AGENT_PATH.exists():
        messagebox.showerror("오류", f"ProctorAgent.exe를 찾을 수 없습니다.\n\n경로: {AGENT_PATH}")
        return

    # 이미 돌아가는 ProctorAgent가 있으면 굳이 또 안 켬
    for p in psutil.process_iter(["name", "exe"]):
        try:
            name = (p.info.get("name") or "").lower()
            exe  = (p.info.get("exe")  or "").lower()
            if "proctoragent.exe" in name or "proctoragent.exe" in exe:
                status_var.set("이미 실행 중인 ProctorAgent가 있습니다.")
                return
        except Exception:
            pass

    try:
        proc = subprocess.Popen([str(AGENT_PATH)])
        status_var.set("에이전트 실행 중")
    except Exception as e:
        messagebox.showerror("실행 오류", str(e))


def stop_agent():
    """이 PC에서 돌아가는 ProctorAgent.exe 프로세스를 전부 종료"""
    global proc
    killed = 0

    for p in psutil.process_iter(["name", "exe"]):
        try:
            name = (p.info.get("name") or "").lower()
            exe  = (p.info.get("exe")  or "").lower()
            if "proctoragent.exe" in name or "proctoragent.exe" in exe:
                p.terminate()
                killed += 1
        except Exception:
            pass

    # 혹시 위에서 못 잡은 경우, UI가 기억하는 proc도 한 번 더 정리
    if proc is not None:
        try:
            if proc.poll() is None:
                proc.terminate()
                killed += 1
        except Exception:
            pass
        proc = None

    if killed > 0:
        status_var.set(f"에이전트 프로세스 {killed}개 종료")
    else:
        status_var.set("실행 중인 에이전트를 찾지 못했습니다.")


def on_close():
    # 창 닫을 때는 그냥 UI만 닫고, 에이전트는 유지하고 싶으면 stop_agent() 호출 안 해도 됨
    # 완전히 끄고 싶으면 아래 주석 풀기:
    # stop_agent()
    root.destroy()


# ==== Tkinter UI ====
root = tk.Tk()
root.title("ProctorAgent 컨트롤러")
root.geometry("340x190")

status_var = tk.StringVar(value="대기 중")

tk.Label(root, text="시험 중 LLM 탐지 에이전트", font=("맑은 고딕", 12, "bold")).pack(pady=10)
tk.Label(root, textvariable=status_var, fg="blue").pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10, fill="x", padx=20)

btn_start = tk.Button(btn_frame, text="에이전트 시작", command=start_agent)
btn_start.pack(side="left", expand=True, fill="x", padx=5)

btn_stop = tk.Button(btn_frame, text="에이전트 종료", command=stop_agent)
btn_stop.pack(side="left", expand=True, fill="x", padx=5)

tk.Label(
    root,
    text=f"에이전트 경로:\n{AGENT_PATH}",
    fg="gray",
    wraplength=300,
    justify="center",
).pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    root.mainloop()

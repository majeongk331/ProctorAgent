import os, time, datetime, ctypes, json
from pathlib import Path
from notifier import notify_all
import yaml
import psutil
import mss
from PIL import Image
import numpy as np
import cv2
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
# ---------- 설정 읽기 (PyInstaller 안전 + 폴백) ----------

import sys
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
def _read_yaml(p: Path):
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_config():
    candidates = []

    # 0) PyInstaller가 푼 임시 리소스 폴더(_MEIPASS) 내부
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / "config.yaml")

    # 1) 실행 파일(.exe)과 같은 폴더
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).parent / "config.yaml")

    # 2) .py 스크립트 위치
    candidates.append(Path(__file__).resolve().parent / "config.yaml")

    # 3) 바탕화면 ProctorAgent 경로(네가 쓰는 경로)
    candidates.append(Path(os.path.expandvars(r"%USERPROFILE%\Desktop\ProctorAgent\config.yaml")))

    for p in candidates:
        if p.exists():
            cfg = _read_yaml(p)
            if cfg:
                return cfg

    # 4) 파일 없어도 바로 돌게 기본값
    return {
        "interval": 3.0,
        "log_dir": os.path.expandvars(r"%USERPROFILE%\Desktop\ProctorAgent\logs"),
        "keywords": ["chatgpt","챗지피티","chat.openai.com","openai","claude","클로드","gemini","제미나이","bard","ai assistant","ask ai"],
        "title_markers": ["chatgpt","챗지피티","openai","claude","클로드","gemini","제미나이","bard","ai"],
        "template_matching": False,
        "ocr_enabled": False,
        "debug_save_all": True,   # 처음엔 캡처 확인용으로 켜둠
    }

CFG = load_config()

INTERVAL = float(CFG.get("interval", 3.0))
LOG_DIR = Path(os.path.expandvars(CFG.get("log_dir", r"%USERPROFILE%\Desktop\ProctorAgent\logs")))
KEYWORDS = [k.lower() for k in CFG.get("keywords", [])]
TITLE_MARKERS = [t.lower() for t in CFG.get("title_markers", [])]
TPL_MATCH = bool(CFG.get("template_matching", False))
OCR_ENABLED = bool(CFG.get("ocr_enabled", False))
DEBUG_SAVE_ALL = bool(CFG.get("debug_save_all", False))

LOG_DIR.mkdir(parents=True, exist_ok=True)
(LOG_DIR / "images").mkdir(exist_ok=True)

CFG = load_config()

INTERVAL = float(CFG.get("interval", 3.0))
# 환경변수(%USERPROFILE% 등) 들어오면 확장
LOG_DIR = Path(os.path.expandvars(CFG.get("log_dir", r"%USERPROFILE%\Desktop\ProctorAgent\logs")))
KEYWORDS = [k.lower() for k in CFG.get("keywords", [])]
TITLE_MARKERS = [t.lower() for t in CFG.get("title_markers", [])]
TPL_MATCH = bool(CFG.get("template_matching", False))
OCR_ENABLED = bool(CFG.get("ocr_enabled", False))
DEBUG_SAVE_ALL = bool(CFG.get("debug_save_all", False))

if OCR_ENABLED:
    import pytesseract
    tess = CFG.get("tesseract_cmd", None)
    if tess and Path(tess).exists():
        pytesseract.pytesseract.tesseract_cmd = tess
    OCR_LANG = CFG.get("ocr_lang","eng+kor")
else:
    pytesseract = None

LOG_DIR.mkdir(parents=True, exist_ok=True)
(LOG_DIR / "images").mkdir(exist_ok=True)


# ---------- 활성 창 제목 (Win32) ----------
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW

def get_active_window_title():
    try:
        hwnd = GetForegroundWindow()
        length = GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    except Exception:
        return ""

# ---------- 프로세스 리스트 ----------
def get_process_names():
    names = []
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name']:
                names.append(p.info['name'].lower())
        except Exception:
            pass
    return names

# ---------- 스크린샷 ----------
def capture_screen_pil():
    with mss.mss() as sct:
        mon = sct.monitors[0]  # 전체화면
        sct_img = sct.grab(mon)
        img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
        return img

# ---------- 템플릿 매칭 ----------
def template_match(img_np, template_path, thr=0.72):
    # 템플릿을 컬러로 읽고 -> 그레이스케일로 변환 (알파 채널 제거)
    tpl = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if tpl is None:
        return False

    # 화면 캡처는 PIL -> numpy라 RGB일 가능성 높음. 그레이스케일로 맞춤.
    if img_np.ndim == 3:
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img_np

    # 템플릿도 그레이스케일
    if tpl.ndim == 3:
        tpl_gray = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
    else:
        tpl_gray = tpl

    # 타입을 uint8로 강제 (matchTemplate 요구사항)
    img_gray = img_gray.astype(np.uint8, copy=False)
    tpl_gray = tpl_gray.astype(np.uint8, copy=False)

    H, W = img_gray.shape[:2]

    # 여러 스케일에서 시도 (템플릿이 화면보다 크면 스킵)
    for scale in [1.2, 1.0, 0.9, 0.8]:
        th, tw = tpl_gray.shape[:2]
        nw, nh = int(tw * scale), int(th * scale)
        if nw < 5 or nh < 5:
            continue
        if nh > H or nw > W:
            continue

        resized = cv2.resize(tpl_gray, (nw, nh),
                             interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR)
        res = cv2.matchTemplate(img_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val >= thr:
            return True

    return False


# ---------- 판단 ----------
def is_suspicious(text_low, title_low, proc_names_low, img_np):
    # 1) 키워드: OCR 또는 텍스트에서
    if any(kw in text_low for kw in KEYWORDS):
        return True, "keyword"
    # 2) 활성 창 제목
    if any(m in title_low for m in TITLE_MARKERS):
        return True, "title"
    # 3) 템플릿 매칭
    if TPL_MATCH:
        tpl_path = BASE_DIR / "templates" / "chatgpt_logo.png"
        if tpl_path.exists() and template_match(img_np, tpl_path):
            return True, "template"
    # 4) 프로세스명(브라우저/앱 자체는 근거 약함 → 보조 신호)
    if any(p in ("chrome.exe","msedge.exe","firefox.exe","opera.exe") for p in proc_names_low):
        # 브라우저만으로는 의심 아님 → title/keyword와 조합되면 강함
        pass
    return False, ""

# ---------- 메인 루프 ----------
def main():
    print("ProctorAgent started. Interval=", INTERVAL)
    while True:
        t0 = time.time()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        title = get_active_window_title()
        title_low = title.lower()
        procs = get_process_names()

        img = capture_screen_pil()
        img_np = np.array(img)

         # ★ 디버그: 무조건 저장해서 캡처 파이프라인 확인
       # if DEBUG_SAVE_ALL:
        #    img.save(LOG_DIR / "images" / f"dbg_{ts}.png")

        # OCR (선택)
        text_low = ""
        if OCR_ENABLED and pytesseract:
            try:
                text = pytesseract.image_to_string(img, lang=OCR_LANG)
                text_low = text.lower()
            except Exception:
                text_low = ""

        suspicious, reason = is_suspicious(text_low, title_low, procs, img_np)

        if suspicious:
            # 저장
            img_path = LOG_DIR / "images" / f"susp_{ts}.png"
            img.save(img_path)
            log_line = {
                "time": ts,
                "reason": reason,
                "title": title,
                "keywords_hit": [kw for kw in KEYWORDS if kw in text_low or kw in title_low],
                "process_sample": procs[:10]
            }
            with open(LOG_DIR / "log.txt","a",encoding="utf-8") as f:
                f.write(json.dumps(log_line, ensure_ascii=False) + "\n")
            
            seat_id = CFG.get("seat_id", "?")
            notify_all(CFG, seat_id, reason, title, img_path)

        # 인터벌 유지
        dt = time.time() - t0
        sleep = INTERVAL - dt
        if sleep > 0:
            time.sleep(sleep)

if __name__ == "__main__":
    main()

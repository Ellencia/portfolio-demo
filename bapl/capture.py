"""데모 바플 서버(8100) 화면을 캡처한다. 화면 맨 위 회사명 칸은 가상 회사명으로 바꿔 찍음 (바플 코드는 안 건드림).

실행: ..\\.venv\\Scripts\\python capture.py          ->  ../img/bapl_<이름>.jpg  (폰 폭 390, 3배 — bapl.html 이 씀)
      ..\\.venv\\Scripts\\python capture.py --desktop ->  shots/<이름>.png      (1440 폭, 2배 — 확인용)
데모 서버는 seed_demo.py 로 만든 가짜 DB 로 띄운다 (README 의 명령).
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
BASE = "http://127.0.0.1:8100"
FAKE = "() => document.querySelectorAll('.brand-sub, .login-brand-org').forEach(e => e.textContent = '한결시스템')"
# 이름: (경로, 찍을 높이 CSS px)
MOBILE = {"flow": ("/flow", 760), "todo": ("/plans/todo", 1150), "order": ("/orders/6", 0), "dash": ("/dashboard", 1250),
          # 1번 장면(히어로) 작은 창들
          "w_order": ("/orders/3/edit", 720), "w_purchase": ("/purchases/1", 720), "w_in": ("/stock/1", 720),
          "w_out": ("/stock/3", 720), "w_proj": ("/projects", 720), "w_tax": ("/tax-invoices?status=matched&period=all", 720)}
DESKTOP = {"flow": "/flow", "orders": "/", "order": "/orders/6", "purchases": "/purchases", "todo": "/plans/todo",
           "plan": "/plans/P26-011", "stock": "/stock", "dashboard": "/dashboard"}

desktop = "--desktop" in sys.argv
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    if desktop:
        out = HERE / "shots"
        out.mkdir(exist_ok=True)
        pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        for name, path in DESKTOP.items():
            pg.goto(BASE + path)
            pg.wait_for_load_state("networkidle")
            pg.evaluate(FAKE)
            pg.screenshot(path=str(out / f"{name}.png"), full_page=True)
            print(name, "ok")
    else:
        out = HERE.parent / "img"
        out.mkdir(exist_ok=True)
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
        for name, (path, h) in MOBILE.items():
            pg.goto(BASE + path)
            pg.wait_for_load_state("networkidle")
            pg.evaluate(FAKE)
            full = pg.evaluate("document.documentElement.scrollHeight")
            clip = {"x": 0, "y": 0, "width": 390, "height": min(h or full, full)}
            pg.screenshot(path=str(out / f"bapl_{name}.jpg"), clip=clip, full_page=True, type="jpeg", quality=88)
            print(name, "높이", clip["height"], "/", full)
    b.close()

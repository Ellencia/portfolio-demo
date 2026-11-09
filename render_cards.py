"""excel.html·harness.html 장면을 폰 크기(1080x1920) PNG 카드로 찍는다. 설치된 크롬 헤드리스만 씀.

실행: python render_cards.py [페이지 이름 ...]  ->  out/cards/excel_1.png ..., out/cards/harness-dark_1.png ...
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT = HERE / "out" / "cards"
# (페이지, 디자인) — 디자인은 harness-themes.css 의 theme-* 이름, None 이면 기본
JOBS = [("excel", None), ("harness", None), ("bapl", None), ("tabrip", None), ("cad", None), ("dl", None), ("forms", None), ("imp", None), ("b2b", None), ("ocr", None), ("harness_a", None), ("harness_b", None), ("harness_c", None), ("harness", "dark"), ("harness", "phone"), ("harness", "memo"), ("harness", "brand")]
only = set(sys.argv[1:])
OUT.mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    for page_name, theme in JOBS:
        name = f"{page_name}-{theme}" if theme else page_name
        if only and name not in only and page_name not in only:
            continue
        src = (HERE / f"{page_name}.html").read_text(encoding="utf-8")
        tmp = HERE / f"_render_{page_name}.html"
        tmp.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
                       '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
                       + src + "</body></html>", encoding="utf-8")
        try:
            for i in range(1, src.count('<section class="scene') + 1):
                pg = browser.new_page(viewport={"width": 360, "height": 640}, device_scale_factor=3)
                errors = []
                pg.on("pageerror", lambda error: errors.append(str(error)))
                pg.goto(tmp.as_uri() + f"?shot={i}" + (f"&theme={theme}" if theme else ""))
                # 형광펜 좌표는 웹 글꼴 로드 뒤 다시 계산된다. 그 작업과 페인트까지 기다린다.
                pg.evaluate("document.fonts.ready.then(() => 1)")
                pg.evaluate("new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
                if errors:
                    raise RuntimeError("페이지 오류: " + "; ".join(errors))
                png = OUT / f"{name}_{i}.png"
                pg.screenshot(path=str(png))
                pg.close()
                print(png.name, "ok", flush=True)
        finally:
            tmp.unlink(missing_ok=True)
    browser.close()

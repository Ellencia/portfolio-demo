"""excel.html·harness.html 장면을 폰 크기(1080x1920) PNG 카드로 찍는다. 설치된 크롬 헤드리스만 씀.

실행: python render_cards.py [페이지 이름 ...]  ->  out/excel_1.png ..., out/harness_1.png ..., out/harness-dark_1.png ...
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "out"
# (페이지, 디자인) — 디자인은 harness-themes.css 의 theme-* 이름, None 이면 기본
JOBS = [("excel", None), ("harness", None), ("bapl", None), ("harness", "dark"), ("harness", "phone"), ("harness", "memo"), ("harness", "brand")]
CHROME = next(p for p in (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
) if p.exists())

only = set(sys.argv[1:])
OUT.mkdir(exist_ok=True)
for page in dict.fromkeys(p for p, _ in JOBS):
    # 아티팩트용 파일엔 문서 머리(doctype·charset)가 없음 → 붙인 사본으로 찍는다 (css·js 를 찾게 같은 폴더에)
    src = (HERE / f"{page}.html").read_text(encoding="utf-8")
    tmp = HERE / f"_render_{page}.html"
    tmp.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
                   + src + "</body></html>", encoding="utf-8")
    for _, theme in [j for j in JOBS if j[0] == page]:
        name = f"{page}-{theme}" if theme else page
        if only and name not in only and page not in only:
            continue
        for i in range(1, src.count('<section class="scene"') + 1):
            png = OUT / f"{name}_{i}.png"
            q = f"?shot={i}" + (f"&theme={theme}" if theme else "")
            subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--window-size=360,640", "--force-device-scale-factor=3",
                            "--virtual-time-budget=6000", f"--screenshot={png}",
                            tmp.as_uri() + q], check=True, capture_output=True)
            print(png.name, "ok" if png.exists() else "실패")
    tmp.unlink()

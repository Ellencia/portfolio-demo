"""my-b2b-apps 포폴 화면 캡처 — seed.js 로 가상 고객사를 넣고 폰 폭(390, 3배)으로 찍는다.

앱 코드는 안 건드리고, 폰 폭에서 찌그러지는 곳만 캡처할 때 CSS 로 덮는다 (FIX).
결과: ../img/b2b_<이름>.jpg + ../img/b2b_boxes.json (강조 상자 좌표, CSS px) + 상태 개수
실행: ..\\.venv\\Scripts\\python capture.py   (my-b2b-apps 를 8718 포트로 직접 띄움)
"""
import json
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "img"
APP = HERE.parents[1] / "my-b2b-apps"
PORT = 8718  # c:/Programming/PORTS.md
BASE = f"http://127.0.0.1:{PORT}"
FIX = """
.filter-container { grid-template-columns: 1fr 1fr !important }
#search-input { grid-column: 1 / -1 }
.controls button, .controls select { font-size: .85rem !important; white-space: nowrap; padding: 8px 10px !important }
header h1 { font-size: 1.2rem !important; white-space: nowrap }
#date-filter { font-size: 12px; max-width: 118px }
.layout-container-wrapper { height: 560px !important }
.form-group-inline label { white-space: nowrap }
#add-printer-from-preset-btn, #add-printer-btn-form { white-space: nowrap }
"""
# 선택자 → 문서 좌표 [x, y, w, h]
BOX = """(sel) => { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect();
  return [Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)]; }"""
# 입력칸의 글자 자리 (타이핑 효과용): [x, y, w, h, 글자 시작 x, 글자 끝 x, 글자 수] — 앞 k 글자는 이미 있던 것
TBOX = """([sel, k]) => { const e = document.querySelector(sel), r = e.getBoundingClientRect(), cs = getComputedStyle(e);
  const c = document.createElement('canvas').getContext('2d'); c.font = cs.font;
  const x0 = r.x + parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), v = e.value;
  return [Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height),
          Math.round(x0 + c.measureText(v.slice(0, k)).width), Math.round(x0 + c.measureText(v).width) + 2, v.length - k]; }"""
# 두 요소를 감싸는 상자
SPAN = """([a, b]) => { const box = s => { const e = document.querySelector(s); return (e.closest('.form-row') || e.closest('.form-group')).getBoundingClientRect(); };
  const r1 = box(a), r2 = box(b);
  return [Math.round(r1.x), Math.round(r1.y + scrollY), Math.round(r1.width), Math.round(r2.bottom - r1.top)]; }"""


def main():
    if socket.socket().connect_ex(("127.0.0.1", PORT)) == 0:
        raise SystemExit(f"{PORT} 포트를 쓰는 서버가 있음 — 닫고 다시")
    OUT.mkdir(exist_ok=True)
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "-b", "127.0.0.1"], cwd=APP,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    boxes = {}
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(BASE + "/index.html", timeout=1)
                break
            except OSError:
                time.sleep(0.25)
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)

            def go(path):
                pg.goto(BASE + path)
                pg.wait_for_load_state("networkidle")
                pg.add_style_tag(content=FIX)
                pg.wait_for_timeout(150)

            def shot(name, h=0, y0=0, **bx):  # y0: 문서의 이 높이부터 찍음 (상자 좌표도 그만큼 올림)
                full = pg.evaluate("document.documentElement.scrollHeight")
                clip = {"x": 0, "y": y0, "width": 390, "height": min(h or full, full - y0)}
                pg.screenshot(path=str(OUT / f"b2b_{name}.jpg"), clip=clip, full_page=True, type="jpeg", quality=88)
                bx = {k: [b[0], b[1] - y0, *b[2:]] for k, b in bx.items()}
                boxes[name] = {"height": clip["height"], **bx}
                print(name, clip["height"])

            go("/select_profile.html")
            boxes["counts"] = pg.evaluate((HERE / "seed.js").read_text(encoding="utf-8"))
            go("/ipmanager/ipmanager.html")
            shot("list", 0, err=pg.evaluate(BOX, "#customer-list li.customer-list-error"), pend=pg.evaluate(BOX, "#customer-list li.customer-list-pending"))

            # 프리셋 장면: 부서 프리셋이 없던 때처럼 칸마다 손으로 (부서를 바꾸면 또) → 프리셋으로 한 번에
            pg.evaluate("() => localStorage.setItem('예시구청_departmentPresets', '[]')")
            go("/ipmanager/ipmanager.html")
            pg.click("#add-customer-fab")
            pg.fill("#customer-name", "한지아")
            pg.fill("#pc-id", "24122")
            hand = [(None, None), ("#customer-department", "민원여권과"), ("#ip-address", "10.20.11.30"), ("#gateway", "10.20.11.1"),
                    ("#dns1", "10.20.0.53"), ("#dns2", "168.126.63.1"), ("#subnet-mask", "255.255.255.0"),
                    ("#customer-department", "세무과"), ("#ip-address", "10.20.12.31"), ("#gateway", "10.20.12.1")]
            for i, (sel, val) in enumerate(hand):
                if sel:  # 칸에 포커스(노란 테두리)만 들어간 빈 장면을 먼저 — 타이핑 효과는 글자 자리만 잘라 쓰므로
                    pg.fill(sel, "")
                    shot(f"hand{i}c", 760)
                    pg.fill(sel, val)
                shot(f"hand{i}", 760, **({"ty": pg.evaluate(TBOX, [sel, 0])} if sel else {}))
            pg.evaluate((HERE / "seed.js").read_text(encoding="utf-8"))  # 프리셋 되돌림
            go("/ipmanager/ipmanager.html")
            pg.click("#add-customer-fab")
            pg.fill("#customer-name", "한지아")
            pg.fill("#pc-id", "24122")
            pg.click("#customer-department")
            pg.wait_for_timeout(150)
            shot("form_a", 760, dept=pg.evaluate(BOX, "#department-autocomplete-results"))
            pg.click('#department-autocomplete-results .autocomplete-item[data-name="세무과"]')
            pg.wait_for_timeout(150)
            pre = pg.input_value("#ip-address")
            shot("form_b0", 760, net=pg.evaluate(SPAN, ["#ip-address", "#subnet-mask"]))
            pg.focus("#ip-address")
            shot("form_bf", 760)
            pg.fill("#ip-address", pre + "31")
            shot("form_b", 760, ty=pg.evaluate(TBOX, ["#ip-address", len(pre)]))
            # 프린터 프리셋: 같은 폼을 프린터 칸 쪽으로 내려서 (버튼이 보이는 창 위쪽 120px 자리에)
            btn = "#add-printer-from-preset-btn"
            pg.add_style_tag(content="body { padding-bottom: 400px }")  # 페이지 끝이 짧아 그림이 덜 차면 아래 프레임이 비침
            y0 = pg.evaluate(BOX, btn)[1] - 262 - 120
            shot("pr0", 760, y0, btn=pg.evaluate(BOX, btn))
            pg.click(btn)
            shot("pr1", 760, y0, sel=pg.evaluate(BOX, "#printer-form-list select"))
            pg.select_option("#printer-form-list select", "2")
            pg.wait_for_timeout(150)
            shot("pr2", 760, y0, form=pg.evaluate(BOX, "#printer-form-list > :last-child"))

            go("/layout/layout.html")
            pg.evaluate("""() => { const w = document.querySelector('.layout-container-wrapper');
              const it = [...document.querySelectorAll('.pc-item')].map(e => e.getBoundingClientRect());
              const cx = (Math.min(...it.map(r => r.left)) + Math.max(...it.map(r => r.right))) / 2,
                    cy = (Math.min(...it.map(r => r.top)) + Math.max(...it.map(r => r.bottom))) / 2, wr = w.getBoundingClientRect();
              w.scrollLeft += cx - (wr.left + wr.width / 2); w.scrollTop += cy - (wr.top + wr.height / 2); }""")
            shot("layout", 760, err=pg.evaluate(BOX, ".pc-item.pc-item-error"), pend=pg.evaluate(BOX, ".pc-item.pc-item-pending"))
            # 끌어 옮기기: 맨 아래 줄 오른쪽 자리(장예준)를 아래 빈 곳으로 (실제 포인터 드래그)
            # drag0 = 그 자리만 뺀 배치도 — 데모에선 그 위로 자리 조각을 커서와 같이 움직임
            it = '.pc-item[data-id="1008"]'
            x, y, w, h = pg.evaluate(BOX, it)
            pg.evaluate(f"document.querySelector('{it}').style.visibility = 'hidden'")
            shot("drag0", 760)
            pg.evaluate(f"document.querySelector('{it}').style.visibility = ''")
            sy = pg.evaluate("scrollY")
            cx, cy = x + w / 2, y - sy + h / 2
            pg.mouse.move(cx, cy)
            pg.mouse.down()
            pg.mouse.move(cx - 80, cy + 120, steps=16)
            pg.mouse.up()
            pg.wait_for_timeout(150)
            shot("drag2", 760, item=pg.evaluate(BOX, it), start=[x, y, w, h])
            # 짧게 누르면 그 PC 상세로
            x, y, w, h = pg.evaluate(BOX, it)
            with pg.expect_navigation():
                pg.mouse.click(x + w / 2, y - pg.evaluate("scrollY") + h / 2)
            pg.wait_for_load_state("networkidle")
            pg.add_style_tag(content=FIX)
            pg.wait_for_timeout(150)
            shot("detail", 0, edit=pg.evaluate(BOX, "#edit-btn"))

            go("/reporter/reporter.html")
            pg.click("#menu-toggle-btn")
            pg.wait_for_timeout(150)
            shot("report_menu", 520, csv=pg.evaluate(BOX, "#export-csv-btn-menu"))
            b.close()
    finally:
        server.terminate()
    (OUT / "b2b_boxes.json").write_text(json.dumps(boxes, ensure_ascii=False, indent=1), encoding="utf-8")
    print(boxes["counts"])


if __name__ == "__main__":
    main()

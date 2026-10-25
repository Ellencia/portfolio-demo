"""바플 포폴 화면 캡처 — 데모 DB 를 새로 만들고, 이야기 단계마다 DB 를 바꿔 가며 폰 폭(390, 3배)으로 찍는다.

단계: s0 시드 → s1 업체 소식(seed_demo.py news) → s2 입고·견적 회신(seed_demo.py arrive)
결과: ../img/bapl_<이름>.jpg + ../img/bapl_boxes.json (바뀐 곳 좌표, CSS px)
화면 맨 위 회사명 칸은 가상 회사명으로 바꿔 찍음 (바플 코드는 안 건드림).
실행: ..\\.venv\\Scripts\\python capture.py   (serve_demo.bat 서버는 닫고 — 이 스크립트가 직접 띄움)
"""
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "img"
BF = HERE.parents[2] / "projects" / "buyflow"
BFPY = str(BF / ".venv" / "Scripts" / "python.exe")
BASE = "http://127.0.0.1:8100"
ENV = {**os.environ, "BUYFLOW_DATA": str(HERE / "data"), "BUYFLOW_DB": str(HERE / "data" / "buyflow.db"), "BUYFLOW_SKIP_AUTH": "1",
       "BUYFLOW_WORK_INBOX": str(HERE / "empty"), "BUYFLOW_Z_ROOT": str(HERE / "empty"), "BUYFLOW_INBOX": str(HERE / "empty")}
FAKE = "() => document.querySelectorAll('.brand-sub, .login-brand-org').forEach(e => e.textContent = '한결시스템')"
# 글자로 요소 찾기: 그 글자를 가진 가장 작은 요소와, 그걸 감싼 카드
BOX = """(q) => { let best = null;
  for (const el of document.querySelectorAll('body *')) {
    const t = el.textContent.replace(/\\s+/g, ' ').trim(); const r = el.getBoundingClientRect();
    if (r.width && t.includes(q) && (!best || r.width * r.height < best.r.width * best.r.height)) best = {el, r}; }
  if (!best) return null;
  const c = best.el.closest('.card, .kpi-card, .flow-group, section, li, tr') || best.el, cr = c.getBoundingClientRect();
  const f = r => [Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)];
  return {el: f(best.r), card: f(cr)}; }"""
# 화면 블록 목록 (띠를 자를 경계용): 폭 넓은 요소들의 y 범위와 첫 글자
BLOCKS = """() => [...document.querySelectorAll('body *')].map(el => { const r = el.getBoundingClientRect();
  return [el.tagName + '.' + String(el.className).split(' ')[0], Math.round(r.x), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height),
          el.textContent.replace(/\s+/g, ' ').trim().slice(0, 24)]; }).filter(b => b[3] >= 250 && b[4] >= 14 && b[4] <= 400)"""

# 단계: {이름: (경로, 찍을 높이 CSS px(0 = 끝까지), 좌표를 잴 글자들)}
STEPS = {
    "s0": {"w_order": ("/orders/3/edit", 720, []), "w_purchase": ("/purchases/1", 720, []), "w_in": ("/stock/1", 720, []),
           "w_out": ("/stock/3", 720, []), "w_proj": ("/projects", 720, []), "w_tax": ("/tax-invoices?status=matched&period=all", 720, []),
           "order_b": ("/orders/3", 0, ["진행 이력"])},
    "s1": {"order_a": ("/orders/3", 0, ["진행 이력", "함체 도장 완료"]), "flow_b": ("/flow", 0, ["키오스크 함체 × 12", "납기 지남"]),
           "todo_b": ("/plans/todo", 0, ["아크릴 커버"]), "dash_b": ("/dashboard", 800, ["입고 대기", "납기 지남 · 미입고"])},
    "s2": {"flow_a": ("/flow", 0, ["납기 지남", "대기번호 표시기 × 8"]), "todo_a": ("/plans/todo", 0, ["아크릴 커버"]),
           "dash_a": ("/dashboard", 800, ["입고 대기", "납기 지남 · 미입고"])},
}


def bf(*args):
    subprocess.run([BFPY, "-X", "utf8", str(HERE / "seed_demo.py"), *args], env=ENV, check=True)


def main():
    if socket.socket().connect_ex(("127.0.0.1", 8100)) == 0:
        raise SystemExit("8100 포트를 쓰는 서버가 있음 — serve_demo.bat 창을 닫고 다시")
    (HERE / "empty").mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    bf()  # s0 시드
    server = subprocess.Popen([BFPY, "-X", "utf8", "-m", "buyflow", "serve", "--db", ENV["BUYFLOW_DB"], "--host", "127.0.0.1",
                               "--port", "8100"], cwd=BF, env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    boxes = {}
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(BASE + "/flow", timeout=1)
                break
            except OSError:
                time.sleep(0.5)
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
            for step, shots in STEPS.items():
                if step == "s1":
                    bf("news")
                elif step == "s2":
                    bf("arrive")
                for name, (path, h, queries) in shots.items():
                    pg.goto(BASE + path)
                    pg.wait_for_load_state("networkidle")
                    pg.evaluate(FAKE)
                    full = pg.evaluate("document.documentElement.scrollHeight")
                    clip = {"x": 0, "y": 0, "width": 390, "height": min(h or full, full)}
                    pg.screenshot(path=str(OUT / f"bapl_{name}.jpg"), clip=clip, full_page=True, type="jpeg", quality=88)
                    boxes[name] = {"height": clip["height"], **{q: pg.evaluate(BOX, q) for q in queries},
                                   **({"blocks": pg.evaluate(BLOCKS)} if queries else {})}
                    print(step, name, clip["height"])
            b.close()
    finally:
        server.terminate()
    (OUT / "bapl_boxes.json").write_text(json.dumps(boxes, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

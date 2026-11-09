"""효과 부품 시계 검사 (FX_DESIGN.md 0단계 합격 기준).

같은 장면을 ① 실제로 재생하며 매 프레임 기록한 화면과 ② 영상 렌더처럼 demoFrame(t) 로 옮긴 화면을 비교한다.
자기 시계로 도는 부품이 있으면 ①과 ②가 어긋나 여기서 걸린다. 끝으로 ③ 카드(?shot)와 영상 마지막 모습도 대조.
화면 = 장면 안 모든 요소의 (불투명도, transform, 직접 든 글자). 시각은 ±50ms 안에서 맞는 순간이 있으면 통과(프레임 출발 오차).

실행: python fx_check.py [페이지.html] [--bad]   (기본 fx_test.html, --bad 는 일부러 어긋나게 해서 검사기가 잡는지 확인)
종료 코드 0 = 통과
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
page_name = args[0] if args else "fx_test.html"
extra = "&bad=1" if "--bad" in sys.argv else ""
src = (HERE / page_name).read_text(encoding="utf-8")
tmp = HERE / f"_check_{Path(page_name).stem}.html"   # 아티팩트용 파일엔 doctype 이 없어서 붙인 사본(css·js 를 찾게 같은 폴더)
tmp.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"></head><body>' + src + "</body></html>", encoding="utf-8")

STATE = """k => { const sc = document.querySelectorAll('.scene')[k];
  return [...sc.querySelectorAll('*')].map(e => { const cs = getComputedStyle(e);
    return [e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList.length ? '.' + [...e.classList].join('.') : ''),
            +cs.opacity, cs.transform, [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.data).join('').trim()] }) }"""
LIVE = "async k => { const state = " + STATE + """;
  const dur = show(k), t0 = performance.now(), out = [];
  await new Promise(res => { const f = () => { const t = performance.now() - t0; out.push([t, state(k)]);
    if (t < dur - 60) requestAnimationFrame(f); else res() }; requestAnimationFrame(f) });
  return [dur, out] }"""
SEEK = "k => { const state = " + STATE + """;
  const dur = demoShow(k), out = [];
  for (let t = 0; t <= dur; t += 8) { demoFrame(t); out.push([t, state(k)]) }
  return [dur, out] }"""


def mat(s):
    return [1, 0, 0, 1, 0, 0] if s == "none" else [float(x) for x in s.split("(", 1)[1].rstrip(")").split(",")][:6]


def diff(a, b):
    """같은 장면의 두 화면에서 다른 요소 이름 목록"""
    bad = []
    for (name, op1, tf1, tx1), (_, op2, tf2, tx2) in zip(a, b):
        m1, m2 = mat(tf1), mat(tf2)
        if abs(op1 - op2) > .04 or tx1 != tx2 or any(abs(x - y) > (.6 if i > 3 else .02) for i, (x, y) in enumerate(zip(m1, m2))):
            bad.append(f"{name} 재생({op1:.2f}, {tx1!r}) 영상({op2:.2f}, {tx2!r})" if tx1 != tx2 or abs(op1 - op2) > .04 else f"{name} 위치")
    return bad


def num(tx):
    """'1,284,000원' 같은 세는 숫자 → 정수, 아니면 None"""
    return int(re.sub(r"\D", "", tx)) if re.fullmatch(r"[\d,]+\D{0,2}", tx) else None


def outside(st, cands):
    """재생 화면 st 에서, 영상이 ±50ms 동안 지나간 범위 밖에 있는 요소 목록(요소마다 따로: 빠르게 변하는 숫자·투명도는 8ms 격자와 딱 안 맞으므로)"""
    bad = []
    for i, (name, op, tf, tx) in enumerate(st):
        cs = [c[i] for c in cands]
        ops, mats, txs = [c[1] for c in cs], [mat(c[2]) for c in cs], [c[3] for c in cs]
        m, ns, n = mat(tf), [num(t) for t in txs], num(tx)
        ok = (min(ops) - .04 <= op <= max(ops) + .04
              and all(min(v) - tol <= x <= max(v) + tol for x, v, tol in zip(m, zip(*mats), (.02,) * 4 + (.6,) * 2))
              and (tx in txs or (n is not None and None not in ns and min(ns) <= n <= max(ns))))
        if not ok:
            bad.append(f"{name} 재생({op:.2f}, {tx!r}) 영상({min(ops):.2f}–{max(ops):.2f}, {sorted(set(txs))[:3]})")
    return bad


fails = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        errs = []
        def open_(q):
            pg = b.new_page(viewport={"width": 360, "height": 640})
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(tmp.as_uri() + q)
            pg.evaluate("document.fonts.ready.then(() => 1)")
            return pg
        live, video = open_("?x=1" + extra), open_("?video=1" + extra)
        n = video.evaluate("demoScenes")
        for k in range(n):
            ldur, lsamp = live.evaluate(LIVE, k)
            vdur, grid = video.evaluate(SEEK, k)
            miss = []
            for t, st in lsamp:
                cands = [g for gt, g in grid if abs(gt - t) <= 50]
                if cands and (d := outside(st, cands)):
                    miss.append((t, d))
            shot = open_(f"?shot={k + 1}" + extra)
            send = shot.evaluate("k => (" + STATE + ")(k)", k)
            shot.close()
            video.evaluate(f"demoFrame({vdur})")
            vend = video.evaluate("k => (" + STATE + ")(k)", k)
            sdiff = diff(send, vend)
            ok = not miss and not sdiff and abs(ldur - vdur) < 1
            fails += not ok
            print(f"장면 {k + 1}: {'통과' if ok else '실패'}  길이 재생 {ldur:.0f}ms / 영상 {vdur:.0f}ms, 프레임 {len(lsamp)}장 중 어긋남 {len(miss)}, 카드≠영상끝 {len(sdiff)}")
            for t, d in miss[:3]:
                print(f"   {t:6.0f}ms  {d[0]}")
            for d in sdiff[:3]:
                print(f"   카드  {d}")
        if errs:
            fails += 1
            print("스크립트 오류:", errs)
        b.close()
finally:
    tmp.unlink(missing_ok=True)
print("결과:", "통과" if not fails else f"실패 {fails}")
sys.exit(1 if fails else 0)

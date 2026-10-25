"""excel.html·harness.html 을 애니메이션 그대로 MP4(1080x1920, H.264)로 만든다.

화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 이어 붙이므로 끊김이 없다.
실행: .venv\\Scripts\\python make_video.py harness [--theme dark] [--fps 30] [--sfx]  ->  out/harness[-dark].mp4
--sfx: demo.js 의 demoSfx() 가 주는 시각에 sfx.py 합성음을 깔고, 장면이 넘어갈 때 휙 소리 (numpy 필요)
"""
import argparse
import io
from fractions import Fraction
from pathlib import Path

import av
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("page", choices=["excel", "harness", "bapl", "tabrip"])
ap.add_argument("--theme", default="", help="harness 디자인: dark / phone / memo / brand")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--sfx", action="store_true", help="효과음 트랙 넣기")
a = ap.parse_args()

name = f"{a.page}-{a.theme}" if a.theme else a.page
src = (HERE / f"{a.page}.html").read_text(encoding="utf-8")
tmp = HERE / f"_video_{a.page}.html"  # 아티팩트용 파일엔 doctype·charset 이 없어서 붙인 사본 (css·js 를 찾게 같은 폴더)
tmp.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"></head><body>' + src + "</body></html>", encoding="utf-8")
mp4 = HERE / "out" / f"{name}.mp4"
mp4.parent.mkdir(exist_ok=True)

try:
    with sync_playwright() as p, av.open(str(mp4), "w") as out:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 360, "height": 640}, device_scale_factor=3)
        page.goto(tmp.as_uri() + "?video=1" + (f"&theme={a.theme}" if a.theme else ""))
        page.evaluate("document.fonts.ready.then(() => 1)")
        st = out.add_stream("libx264", rate=a.fps)
        st.width, st.height, st.pix_fmt = 1080, 1920, "yuv420p"
        st.options = {"crf": "21", "preset": "medium"}
        if a.sfx:
            import numpy as np
            import sfx
            ast = out.add_stream("aac", rate=sfx.SR, layout="stereo")
        frames, events = 0, []
        for i in range(page.evaluate("demoScenes")):
            dur = page.evaluate(f"demoShow({i})")
            if a.sfx:
                t0 = frames / a.fps
                events += [(t0 + ms / 1000, n) for ms, n in page.evaluate("demoSfx()")]
                if i:
                    events.append((t0 - 0.15, "whoosh"))
            for f in range(round(dur / 1000 * a.fps)):
                page.evaluate(f"demoFrame({f * 1000 / a.fps})")
                png = page.screenshot(type="png")
                img = next(av.open(io.BytesIO(png), format="png_pipe").decode(video=0)).reformat(format="yuv420p")
                img.pts, img.time_base = frames, Fraction(1, a.fps)  # 없으면 재생기가 길이를 0초로 읽음
                img.pict_type = av.video.frame.PictureType.NONE  # PNG 에서 온 프레임은 전부 키프레임 표시라 압축이 안 됨
                for pkt in st.encode(img):
                    out.mux(pkt)
                frames += 1
            print(f"장면 {i + 1} {dur / 1000:.1f}초", flush=True)
        for pkt in st.encode():
            out.mux(pkt)
        if a.sfx:
            pcm = sfx.mix(events, frames / a.fps)
            for k in range(0, pcm.shape[1], 1024):
                fr = av.AudioFrame.from_ndarray(np.ascontiguousarray(pcm[:, k:k + 1024]), format="fltp", layout="stereo")
                fr.sample_rate, fr.pts, fr.time_base = sfx.SR, k, Fraction(1, sfx.SR)
                for pkt in ast.encode(fr):
                    out.mux(pkt)
            for pkt in ast.encode():
                out.mux(pkt)
            print(f"효과음 {len(events)}개", flush=True)
        browser.close()
    print(f"{mp4.name}  {frames} 프레임 = {frames / a.fps:.1f}초")
finally:
    tmp.unlink(missing_ok=True)

"""excel.html·harness.html 을 애니메이션 그대로 MP4(1080x1920, H.264)로 만든다.

화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 이어 붙이므로 끊김이 없다.
실행: .venv\\Scripts\\python make_video.py harness [--theme dark] [--fps 30] [--sfx]  ->  out/video/harness[-dark].mp4
--sfx: demo.js 의 demoSfx() 가 주는 시각에 sfx.py 합성음을 깔고, 장면이 넘어갈 때 휙 소리 (numpy 필요)
"""
import argparse
import io
import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

import av
from av.video.reformatter import VideoReformatter
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
ap = argparse.ArgumentParser()
ap.add_argument("page", choices=["excel", "harness", "harness_a", "harness_b", "harness_c", "bapl", "tabrip", "cad", "dl", "forms", "imp", "b2b", "ocr"])
ap.add_argument("--theme", default="", help="harness 디자인: dark / phone / memo / brand")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--sfx", action="store_true", help="효과음 트랙 넣기")
ap.add_argument("--sfx-db", type=float, default=0, help="효과음 음량 조절(dB). 음악은 그대로")
ap.add_argument("--bgm", nargs="?", const="waltz",
                help="배경음: waltz·arp = 합성 기타 반주(기본 waltz), bgm/*.mid = 직접 쓴 곡(FluidSynth 렌더), 그 밖엔 음악 파일 경로(music/ 에 두고 커밋 안 함)")
a = ap.parse_args()

name = f"{a.page}-{a.theme}" if a.theme else a.page
src = (HERE / f"{a.page}.html").read_text(encoding="utf-8")
tmp = HERE / f"_video_{a.page}.html"  # 아티팩트용 파일엔 doctype·charset 이 없어서 붙인 사본 (css·js 를 찾게 같은 폴더)
tmp.write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"></head><body>' + src + "</body></html>", encoding="utf-8")
mp4 = HERE / "out" / "video" / f"{name}.mp4"
mp4.parent.mkdir(exist_ok=True)

try:
    with sync_playwright() as p, av.open(str(mp4), "w") as out:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 360, "height": 640}, device_scale_factor=3)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(tmp.as_uri() + "?video=1" + (f"&theme={a.theme}" if a.theme else ""))
        page.evaluate("document.fonts.ready.then(() => 1)")
        page.evaluate("new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        if errors:
            raise RuntimeError("페이지 오류: " + "; ".join(errors))
        st = out.add_stream("libx264", rate=a.fps)
        st.width, st.height, st.pix_fmt = 1080, 1920, "yuv420p"
        st.options = {"crf": "21", "preset": "medium"}
        st.codec_context.color_range = 1  # MPEG limited range
        reformatter = VideoReformatter()
        if a.sfx or a.bgm:
            import numpy as np
            import sfx
            ast = out.add_stream("aac", rate=sfx.SR, layout="stereo")
        frames, events = 0, []
        cover = page.evaluate("!!document.getElementById('cover')")  # 페이지에 표지가 있으면 맨 앞에: 카톡 미리보기 = 첫 프레임
        for i in range(-1 if cover else 0, page.evaluate("demoScenes")):
            dur = 1034 if i < 0 else page.evaluate(f"demoShow({i})")  # 표지 1.03초: ocr 배경음 첫 음까지(♩=58 한 박)
            page.evaluate(f"document.body.classList.toggle('cover-on', {'true' if i < 0 else 'false'})")
            if a.sfx and i >= 0:
                t0 = frames / a.fps
                events += [(t0 + ms / 1000, n) for ms, n in page.evaluate("demoSfx()")]
                if frames:
                    events.append((t0 - 0.15, "whoosh"))
            for f in range(round(dur / 1000 * a.fps)):
                page.evaluate(f"demoFrame({f * 1000 / a.fps})")
                png = page.screenshot(type="png")
                # PNG 디코더의 full-range 태그를 YUV로 그대로 넘기면 MP4에서 대비가 달라진다.
                with Image.open(io.BytesIO(png)) as capture:
                    rgb = av.VideoFrame.from_image(capture.convert("RGB"))
                img = reformatter.reformat(rgb, format="yuv420p", src_color_range="JPEG", dst_color_range="MPEG")
                img.color_range = 1
                img.pts, img.time_base = frames, Fraction(1, a.fps)  # 없으면 재생기가 길이를 0초로 읽음
                img.pict_type = av.video.frame.PictureType.NONE  # PNG 에서 온 프레임은 전부 키프레임 표시라 압축이 안 됨
                for pkt in st.encode(img):
                    out.mux(pkt)
                frames += 1
            print(f"장면 {i + 1} {dur / 1000:.1f}초", flush=True)
        for pkt in st.encode():
            out.mux(pkt)
        if a.sfx or a.bgm:
            music = a.bgm
            if music and music.endswith(".mid"):  # 직접 쓴 곡(bgm/) → FluidSynth 로 wav
                wav = Path(tempfile.gettempdir()) / "portfolio_bgm.wav"
                subprocess.run([os.environ.get("FLUIDSYNTH_EXE", r"C:\Programming\tools\fluidsynth\bin\fluidsynth.exe"),
                                "-ni", "-q", "-g", "0.55", "-r", str(sfx.SR), "-F", str(wav),
                                os.environ.get("BGM_SF2", r"C:\Programming\Projects\guitar-transcriber\assets\FluidR3 GM2-2.SF2"), music],
                               check=True)
                music = str(wav)
            if music and music not in sfx.STYLES:  # 음악 파일 → SR 모노
                rs, chunks = av.AudioResampler(format="flt", layout="mono", rate=sfx.SR), []
                with av.open(music) as f:
                    for fr in f.decode(audio=0):
                        chunks += [o.to_ndarray().ravel() for o in rs.resample(fr)]
                chunks += [o.to_ndarray().ravel() for o in rs.resample(None)]
                music = np.concatenate(chunks)
            pcm = sfx.mix(events, frames / a.fps, music=music, sfx_db=a.sfx_db)
            for k in range(0, pcm.shape[1], 1024):
                fr = av.AudioFrame.from_ndarray(np.ascontiguousarray(pcm[:, k:k + 1024]), format="fltp", layout="stereo")
                fr.sample_rate, fr.pts, fr.time_base = sfx.SR, k, Fraction(1, sfx.SR)
                for pkt in ast.encode(fr):
                    out.mux(pkt)
            for pkt in ast.encode():
                out.mux(pkt)
            print(f"효과음 {len(events)}개", flush=True)
        browser.close()
        if errors:
            raise RuntimeError("페이지 오류: " + "; ".join(errors))
    print(f"{mp4.name}  {frames} 프레임 = {frames / a.fps:.1f}초")
finally:
    tmp.unlink(missing_ok=True)

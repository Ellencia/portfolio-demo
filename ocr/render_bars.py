"""악보 판독 데모용 그림: score-ocr(비공개)의 미뉴에트 원출력·고친 판에서 몇 마디만 잘라 MuseScore 로 그린다.

실행: python ocr/render_bars.py  ->  img/ocr_*.png, img/ocr_paper_*.jpg
교재 사진은 공개 저장소에 넣지 않는다. "사진"은 고친 판 렌더에 종이 질감을 입힌 설명용 그림이다.
"""
import copy
import random
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).parent
IMG = HERE.parent / "img"
SRC = Path(r"c:/Programming/Projects/score-ocr/minuet")
RAW = SRC / "omr" / "minuet_scan.mvt1.musicxml"  # Audiveris 원출력
FIX = SRC / "Minuet_mscz.musicxml"  # 사람이 고친 판
M3 = Path(r"c:/Programming/Projects/score-ocr/minuet3b")  # 처리 단계별 파일이 다 남은 곡
MUSE = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"


def clip(src, bars, out, fingering=None, mm=None, keep_dir=False):
    """bars 번째 마디만 남긴 MusicXML. 앞 마디들의 박자·조표·음자리표는 첫 마디로 옮기고 fingering={(마디, 음 번호): "3"} 은 손으로 얹는다.
    mm = 보표 높이(mm): 한 마디가 쪽 폭을 다 채우면 폰 화면에서 작아져서 키울 때. keep_dir = 셈여림 남기기."""
    tree = ET.parse(src)
    root = tree.getroot()
    for tag in ("work", "movement-number", "movement-title", "identification", "defaults", "credit"):
        for e in root.findall(tag):
            root.remove(e)
    if mm:
        d = ET.fromstring(f"<defaults><scaling><millimeters>{mm}</millimeters><tenths>40</tenths></scaling></defaults>")
        root.insert(list(root).index(root.find("part-list")), d)
    for tag in ("part-name", "part-abbreviation"):
        for e in root.iter(tag):
            e.set("print-object", "no")
    part = root.find("part")
    seen, kept = {}, []
    for i, m in enumerate(list(part.findall("measure"))):
        if i <= bars[0]:
            for attrs in m.findall("attributes"):  # 한 마디에 여러 개일 수 있음
                for a in attrs:
                    seen[a.tag] = a
        if i in bars:
            kept.append(m)
        part.remove(m)
    for n, m in enumerate(kept):
        for tag in ("print", "barline") if keep_dir else ("print", "direction", "barline"):
            for e in m.findall(tag):
                m.remove(e)
        for e in m.findall("note"):
            for nt in e.findall("notations"):
                for tech in nt.findall("technical"):
                    nt.remove(tech)  # 운지는 아래 fingering 으로만 (OCR 찌꺼기 빼기)
        if n == 0:
            for attrs in m.findall("attributes"):
                m.remove(attrs)
            a = ET.Element("attributes")
            for tag in ("divisions", "key", "time", "clef"):
                if tag in seen:
                    a.append(copy.deepcopy(seen[tag]))
            m.insert(0, a)
        part.append(m)
    for (bar, idx), text in (fingering or {}).items():
        note = kept[bars.index(bar)].findall("note")[idx]
        nt = note.find("notations")
        if nt is None:
            nt = ET.SubElement(note, "notations")
        ET.SubElement(ET.SubElement(nt, "technical"), "fingering").text = text
    tree.write(out, encoding="utf-8", xml_declaration=True)


def render(xml, png):
    """MuseScore 렌더 → 잉크 둘레로 자른 흰 배경 PNG."""
    subprocess.run([MUSE, "-r", "300", "-o", str(png), str(xml)], check=True, timeout=100, capture_output=True)
    page = Image.open(png.with_name(f"{png.stem}-1.png")).convert("RGBA")
    white = Image.new("RGBA", page.size, "white")
    white.alpha_composite(page)
    img = white.convert("L")
    box = ImageChops.invert(img).point(lambda v: 255 if v > 40 else 0).getbbox()
    pad = 14
    return squeeze(img.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), box[2] + pad, box[3] + pad)))


def squeeze(img, keep=60):
    """줄 사이 빈 칸을 keep 픽셀로 줄인다 (MuseScore 는 쪽 크기 기준으로 줄을 벌림)."""
    W, H = img.size
    rows, blank = [], 0
    for y in range(H):
        row = img.crop((0, y, W, y + 1))
        blank = blank + 1 if ImageChops.invert(row).point(lambda v: 255 if v > 40 else 0).getbbox() is None else 0
        if blank <= keep:
            rows.append(row)
    out = Image.new("L", (W, len(rows)), 255)
    for y, row in enumerate(rows):
        out.paste(row, (0, y))
    return out


def paper(img, seed):
    """폰으로 찍은 종이처럼: 누런 바탕, 살짝 기울임, 한쪽 그늘, 흐림 (설명용, 실제 사진 아님)."""
    rnd = random.Random(seed)
    W, H = img.size
    pad = 60
    base = Image.new("L", (W + pad * 2, H + pad * 2), 255)
    base.paste(img, (pad, pad))
    base = base.rotate(-1.1, resample=Image.BICUBIC, fillcolor=255).filter(ImageFilter.GaussianBlur(1.1))
    W, H = base.size
    tint = Image.new("RGB", (W, H), (246, 241, 226))
    d = ImageDraw.Draw(tint)
    for x in range(W):  # 오른쪽으로 갈수록 그늘
        k = 1 - 0.14 * (x / W) ** 2
        d.line([(x, 0), (x, H)], fill=(int(246 * k), int(241 * k), int(226 * k)))
    for _ in range(3):  # 뒷면 비침 몇 줄
        y = rnd.randrange(H)
        d.line([(0, y), (W, y + rnd.randrange(-6, 6))], fill=(232, 226, 210), width=2)
    grain = Image.effect_noise((W, H), 9).convert("L")
    tint = ImageChops.multiply(tint, Image.merge("RGB", [grain.point(lambda v: 225 + v // 9)] * 3))
    return ImageChops.multiply(tint, Image.merge("RGB", [base] * 3))


def read_variants():
    """3번 장면 "여섯 번 읽기"의 사진 6장: 실제 실행처럼 회색 한 장 + 흑백 문턱 110–170 다섯 장 (설명용, 그늘 진 종이 그림에 적용)."""
    src = Image.open(IMG / "ocr_cover_paper.jpg").convert("L").crop((40, 20, 1120, 380))
    W, H = src.size
    shade = Image.new("L", (W, H))
    ImageDraw.Draw(shade)
    shade.putdata([int(255 * (1 - 0.42 * (x / W) ** 1.6)) for _ in range(H) for x in range(W)])  # 오른쪽 그늘: 문턱 높은 판에서 검게 번짐
    dim = ImageChops.multiply(src, shade).filter(ImageFilter.GaussianBlur(2.2))
    size = (660, 220)
    src.convert("RGB").resize(size, Image.LANCZOS).save(IMG / "ocr_read_1.jpg", quality=86)
    for n, t in enumerate((110, 125, 140, 155, 170), start=2):
        dim.point(lambda v: 255 if v > t else 0).resize(size, Image.LANCZOS).convert("RGB").save(IMG / f"ocr_read_{n}.jpg", quality=86)


JOBS = [  # 이름, 원본, 마디(0부터), 얹을 운지, 종이?, 보표 높이
    ("ocr_cover_paper", FIX, [1, 2], None, True, 11),
    ("ocr_page_paper", FIX, [1, 2, 3, 4], None, True, 11),
    ("ocr_page_raw", RAW, [1, 2, 3, 4], None, False, 11),
    # 2번 장면: 미뉴에트 3번 79마디의 처리 단계별 판. 음표만 읽음(omr_fix) → 사진과 맞춰 음 고침(apply_fixes) → 표시 옮겨 붙임(transplant)
    ("ocr_m79_paper", M3 / "Minuet3_fixed.musicxml", [78], None, True, 13),
    ("ocr_m79_1", M3 / "minuet3_omr.musicxml", [78], None, False, 13),
    ("ocr_m79_2", M3 / "minuet3_judged.musicxml", [78], None, False, 13),
    ("ocr_m79_3", M3 / "Minuet3_fixed.musicxml", [78], None, False, 13),
]
KEEP_DIR = {"ocr_m79_paper", "ocr_m79_3"}

if __name__ == "__main__":
    for old in IMG.glob("ocr_*"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        for name, src, bars, fing, is_paper, mm in JOBS:
            xml, png = Path(tmp) / f"{name}.musicxml", Path(tmp) / f"{name}.png"
            clip(src, bars, xml, fing, mm, name in KEEP_DIR)
            img = render(xml, png)
            if is_paper:
                paper(img, name).save(IMG / f"{name}.jpg", quality=86)
            else:
                img.save(IMG / f"{name}.png", optimize=True)
            print(name, img.size)
    read_variants()

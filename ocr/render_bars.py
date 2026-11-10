"""악보 판독 데모용 그림: 비제 「하바네라」(저작권 끝남) 1883년 Choudens 판 5–8마디.

- 사진(ocr_page_paper, ocr_bar_paper): habanera_bars5-8.jpg 스캔에 폰 사진 효과를 입힌 설명용 그림
  원본 https://archive.org/details/carmenopracomi00bize PDF 57쪽
- 판독 결과(ocr_page_raw, ocr_bar_1): habanera_omr.mxl = 그 스캔을 Audiveris 로 읽은 원출력 그대로
- 2·3차(ocr_bar_2, ocr_bar_3): 7마디 노래 줄을 손으로 적은 설명용 그림. 파이프라인을 돌린 결과가 아니고, 스타카토·셈여림은 악보에 없는데 넣음

실행: python ocr/render_bars.py  ->  img/ocr_*
"""
import copy
import random
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).parent
IMG = HERE.parent / "img"
SCAN = HERE / "habanera_bars5-8.jpg"
OMR = HERE / "habanera_omr.mxl"
VOICE, PIANO = "P10", "P11"  # 5–8마디에서 노래와 피아노가 들어간 파트. 원출력은 노래를 파트 셋에 흩어 놓음
BAR7_BOX = (965, 30, 1405, 165)  # 스캔에서 7마디 노래 줄
MUSE = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"


def clip(src, bars, out, keep, mm=None, width=None):
    """keep 파트의 bars 번째 마디만 남긴 MusicXML. 앞 마디들의 박자·조표·음자리표는 첫 마디로 옮긴다."""
    tree = ET.parse(src)
    root = tree.getroot()
    for tag in ("work", "movement-number", "movement-title", "identification", "defaults", "credit"):
        for e in root.findall(tag):
            root.remove(e)
    if mm:  # width = 쪽 폭: 마디들이 한 줄에 들어가게. 없으면 기본 쪽(한 마디가 쪽 폭을 채움)
        wide = f"<page-layout><page-height>2000</page-height><page-width>{width}</page-width></page-layout>" if width else ""
        d = ET.fromstring(f"<defaults><scaling><millimeters>{mm}</millimeters><tenths>40</tenths></scaling>{wide}</defaults>")
        root.insert(list(root).index(root.find("part-list")), d)
    for e in root.iter("part-name"):
        e.text = ""  # 원출력의 "du palple." 같은 찌꺼기
    for sp in root.iter("score-part"):
        for tag in ("part-abbreviation", "part-name-display", "part-abbreviation-display"):
            for e in sp.findall(tag):
                sp.remove(e)
    plist = root.find("part-list")
    for sp in plist.findall("score-part"):
        if sp.get("id") not in keep:
            plist.remove(sp)
    for pg in plist.findall("part-group"):
        plist.remove(pg)
    for part in root.findall("part"):
        if part.get("id") not in keep:
            root.remove(part)
            continue
        seen, kept = {}, []
        for i, m in enumerate(list(part.findall("measure"))):
            if i <= bars[0]:
                for attrs in m.findall("attributes"):  # 한 마디에 여러 개일 수 있음. clef 는 보표마다 하나씩
                    for tag in {a.tag for a in attrs}:
                        seen[tag] = attrs.findall(tag)
            if i in bars:
                kept.append(m)
            part.remove(m)
        for n, m in enumerate(kept):
            for tag in ("print", "direction", "barline"):
                for e in m.findall(tag):
                    m.remove(e)
            if n == 0:
                for attrs in m.findall("attributes"):
                    m.remove(attrs)
                a = ET.Element("attributes")
                for tag in ("divisions", "key", "time", "staves", "clef"):
                    a.extend(copy.deepcopy(x) for x in seen.get(tag, []))
                m.insert(0, a)
            part.append(m)
    tree.write(out, encoding="utf-8", xml_declaration=True)


def note(step, oct_, dur, kind, alter=None, tuplet=None, marks=""):
    alt = f"<alter>{alter}</alter>" if alter else ""
    tm = "<time-modification><actual-notes>3</actual-notes><normal-notes>2</normal-notes></time-modification>" if tuplet else ""
    tup = f'<tuplet type="{tuplet}"/>' if tuplet in ("start", "stop") else ""
    nt = f"<notations>{tup}{marks}</notations>" if tup or marks else ""
    return f"<note><pitch><step>{step}</step>{alt}<octave>{oct_}</octave></pitch><duration>{dur}</duration><voice>1</voice><type>{kind}</type>{tm}{nt}</note>"


def bar7(out, marks, mm):
    """7마디 노래 줄. marks = 슬러·스타카토·셈여림까지(설명용)."""
    s0, s1 = ('<slur type="start" number="1"/>', '<slur type="stop" number="1"/>') if marks else ("", "")
    st = "<articulations><staccato/></articulations>" if marks else ""
    dyn = '<direction placement="below"><direction-type><dynamics><p/></dynamics></direction-type></direction>' if marks else ""
    notes = (note("F", 4, 80, "16th", tuplet="start", marks=s0) + note("G", 4, 80, "16th", tuplet="mid")
             + note("F", 4, 80, "16th", tuplet="stop", marks=s1) + note("E", 4, 120, "16th", marks=s0)
             + note("F", 4, 120, "16th", marks=s1) + note("G", 4, 240, "eighth", marks=st) + note("F", 4, 240, "eighth", marks=st))
    Path(out).write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1"><defaults><scaling><millimeters>{mm}</millimeters><tenths>40</tenths></scaling></defaults>
<part-list><score-part id="P1"><part-name print-object="no">x</part-name></score-part></part-list>
<part id="P1"><measure number="7"><attributes><divisions>480</divisions><key><fifths>-1</fifths></key><time><beats>2</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
{dyn}{notes}</measure></part></score-partwise>""", encoding="utf-8")


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
        # 왼쪽 묶음줄은 빈 칸으로 침: 파트 사이를 줄여도 세로로 이어짐
        blank = blank + 1 if ImageChops.invert(row.crop((W // 8, 0, W, 1))).point(lambda v: 255 if v > 40 else 0).getbbox() is None else 0
        if blank <= keep:
            rows.append(row)
    out = Image.new("L", (W, len(rows)), 255)
    for y, row in enumerate(rows):
        out.paste(row, (0, y))
    return out


def photo(img, seed, angle=-1.0):
    """스캔을 폰으로 찍은 듯이: 살짝 기울임, 한쪽 그늘, 흐림, 잡티 (설명용, 실제 사진 아님)."""
    rnd = random.Random(seed)
    W, H = img.size
    fill = img.resize((1, 1)).getpixel((0, 0))
    out = img.rotate(angle, resample=Image.BICUBIC, fillcolor=fill).filter(ImageFilter.GaussianBlur(1.0))
    shade = Image.new("L", (W, H))
    far = rnd.uniform(.72, .78)
    shade.putdata([int(255 * (1 - (1 - far) * (x / W) ** 1.5) * (1 - .05 * (y / H))) for y in range(H) for x in range(W)])
    grain = Image.effect_noise((W, H), 7).convert("L").point(lambda v: 228 + v // 10)
    return ImageChops.multiply(ImageChops.multiply(out, Image.merge("RGB", [shade] * 3)), Image.merge("RGB", [grain] * 3))


def read_variants(src):
    """3번 장면 "여섯 번 읽기"의 사진 6장: 회색 한 장 + 흑백 문턱 다섯 장 (설명용)."""
    g = src.convert("L")
    size = (660, 220)
    g.convert("RGB").resize(size, Image.LANCZOS).save(IMG / "ocr_read_1.jpg", quality=86)
    for n, t in enumerate((95, 115, 135, 155, 175), start=2):
        g.point(lambda v: 255 if v > t else 0).resize(size, Image.LANCZOS).convert("RGB").save(IMG / f"ocr_read_{n}.jpg", quality=86)


if __name__ == "__main__":
    # Do not delete independently generated MusicXML/SVG edit examples.
    scan = Image.open(SCAN).convert("RGB")
    page = photo(scan, "page")
    page.resize((1400, round(1400 * page.height / page.width)), Image.LANCZOS).save(IMG / "ocr_page_paper.jpg", quality=86)
    photo(scan.crop(BAR7_BOX).resize((1200, round(1200 * 135 / 440)), Image.LANCZOS), "bar", -.8).save(IMG / "ocr_bar_paper.jpg", quality=88)
    read_variants(page)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        raw = t / "omr.xml"
        with zipfile.ZipFile(OMR) as z:
            raw.write_bytes(z.read("hab_test.xml"))
        clip(raw, [4, 5, 6, 7], t / "page.musicxml", {VOICE, PIANO}, 7, 2600)
        clip(raw, [6], t / "bar1.musicxml", {VOICE}, 13)
        bar7(t / "bar2.musicxml", False, 13)
        bar7(t / "bar3.musicxml", True, 13)
        for src, name in (("page", "ocr_page_raw"), ("bar1", "ocr_bar_1"), ("bar2", "ocr_bar_2"), ("bar3", "ocr_bar_3")):
            img = render(t / f"{src}.musicxml", t / f"{src}.png")
            img.save(IMG / f"{name}.png", optimize=True)
            print(name, img.size)

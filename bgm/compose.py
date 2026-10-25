"""영상 배경음 후보 — 직접 쓴 멜로디·코드를 MIDI 로 (저작권 걱정 없음). 영상 길이(~95초)보다 길게 만들고 make_video 가 잘라 페이드.

실행: python bgm/compose.py          → bgm/*.mid (커밋) + bgm/*.wav (들어 보기용, 커밋 안 함)
영상: python make_video.py b2b --sfx --bgm bgm/musicbox_waltz.mid   (.mid 는 FluidSynth 로 그 자리에서 렌더)
필요: pretty_midi, FluidSynth(FLUIDSYNTH_EXE), GM 사운드폰트(BGM_SF2) — 기본값은 이 PC 경로
"""
import os
import random
import subprocess
import wave
from pathlib import Path

import numpy as np
import pretty_midi as pm

HERE = Path(__file__).parent
FS = os.environ.get("FLUIDSYNTH_EXE", r"C:\Programming\tools\fluidsynth\bin\fluidsynth.exe")
SF2 = os.environ.get("BGM_SF2", r"C:\Programming\Projects\guitar-transcriber\assets\FluidR3 GM2-2.SF2")
N = pm.note_name_to_number


def bars(spec, beats):
    """"C G Am F" → 마디마다 [(근음, 장/단, 박)]"""
    return [[(c[:-1], "m", beats) if c.endswith("m") else (c, "", beats)] for c in spec.split()]


# 멜로디: 마디마다 (음, 박 길이), None 은 쉼
MEL_C = [  # 4/4 C장조 — 마지막 마디는 끝맺음
    [("G4", 1), ("C5", .5), ("E5", .5), ("G5", 1.5), ("E5", .5)],
    [("D5", 1), ("B4", .5), ("D5", .5), ("G5", 2)],
    [("A5", .5), ("G5", .5), ("E5", 1), ("C5", .5), ("E5", .5), ("A4", 1)],
    [("F5", 1.5), ("E5", .5), ("D5", 1), ("C5", 1)],
    [("G4", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("C6", 1), ("B5", .5), ("A5", .5)],
    [("G5", 1.5), ("D5", .5), ("B4", 1), ("D5", 1)],
    [("A5", 1), ("G5", .5), ("F5", .5), ("E5", 1), ("D5", 1)],
    [("C5", 3), (None, 1)],
    [("E5", .5), ("G5", .5), ("C6", 3)],
]
CH_C = bars("C G Am F C G F C C", 4)
CH_C[6] = [("F", "", 2), ("G", "", 2)]

MEL_F = [  # 4/4 F장조
    [("C5", .5), ("F5", .5), ("A5", .5), ("F5", .5), ("C6", 1), ("A5", 1)],
    [("G5", .5), ("E5", .5), ("C5", .5), ("E5", .5), ("G5", 2)],
    [("F5", .5), ("D5", .5), ("A4", .5), ("D5", .5), ("F5", 1), ("A5", 1)],
    [("A#5", 1.5), ("A5", .5), ("G5", 1), ("F5", 1)],
    [("C5", .5), ("F5", .5), ("A5", .5), ("C6", .5), ("D6", 1), ("C6", 1)],
    [("A#5", .5), ("A5", .5), ("G5", .5), ("E5", .5), ("C5", 2)],
    [("D5", 1), ("G5", 1), ("E5", 1), ("C5", 1)],
    [("F5", 3), (None, 1)],
    [("C5", .5), ("A4", .5), ("F5", 3)],
]
CH_F = bars("F C Dm A# F C A# F F", 4)
CH_F[6] = [("A#", "", 2), ("C", "", 2)]

W_G = [  # 3/4 G장조 왈츠 A
    [("B4", 1), ("D5", 1), ("G5", 1)], [("F#5", 1.5), ("E5", .5), ("D5", 1)], [("A4", 1), ("D5", 1), ("F#5", 1)], [("E5", 2), ("D5", 1)],
    [("G5", 1), ("B5", 1), ("A5", 1)], [("G5", 1.5), ("E5", .5), ("C5", 1)], [("D5", 1), ("F#5", 1), ("A5", 1)], [("G5", 2), ("F#5", 1)],
    [("B5", 1), ("A5", 1), ("G5", 1)], [("D5", 2), ("B4", 1)], [("A4", 1), ("D5", 1), ("F#5", 1)], [("E5", 1.5), ("F#5", .5), ("G5", 1)],
    [("E5", 1), ("G5", 1), ("C6", 1)], [("B5", 1), ("A5", 1), ("F#5", 1)], [("G5", 3)], [(None, 3)]]
WC_G = bars("G G D D Em C D D G G D Em C D G G", 3)
W_G_B = [  # 왈츠 B (단조 쪽으로, 끝에 A장조로 띄움)
    [("B5", 1.5), ("A5", .5), ("G5", 1)], [("E5", 2), ("G5", 1)], [("E5", 1), ("G5", 1), ("C6", 1)], [("B5", 2), ("A5", 1)],
    [("G5", 1), ("B5", 1), ("D6", 1)], [("D6", 1.5), ("C6", .5), ("B5", 1)], [("A5", 1), ("F#5", 1), ("D5", 1)], [("A5", 3)],
    [("B5", 1.5), ("A5", .5), ("G5", 1)], [("E5", 2), ("B4", 1)], [("C5", 1), ("E5", 1), ("G5", 1)], [("C6", 2), ("B5", 1)],
    [("A5", 1), ("C#6", 1), ("E6", 1)], [("E6", 1.5), ("D6", .5), ("C#6", 1)], [("D6", 1), ("A5", 1), ("F#5", 1)], [("E5", 1), ("F#5", 1), ("A5", 1)]]
WC_G_B = bars("Em Em C C G G D D Em Em C C A A D D", 3)


def chord_notes(root, q, octave):
    r = N(f"{root}{octave}")
    return [r, r + (3 if q == "m" else 4), r + 7]


def inst(m, prog, drum=False):
    """같은 악기는 트랙 하나로"""
    for i in m.instruments:
        if i.program == prog and i.is_drum == drum:
            return i
    m.instruments.append(pm.Instrument(prog, is_drum=drum))
    return m.instruments[-1]


def part(m, b0, bpm, mel=(), chords=(), lead=None, lead_oct=0, lead_vel=1.0, comp=None, style="", bass=None, drums=False, swing=0.0, seed=1):
    """한 구간을 m 의 박 b0 부터 써 넣는다"""
    random.seed(seed * 1000 + b0)
    beat = 60 / bpm
    t = lambda b: (b + b0 + (swing if ((b + b0) * 2) % 2 == 1 else 0)) * beat + random.uniform(-.008, .008)  # 뒤 8분을 늦춤
    b = 0
    for bar in mel:
        for p, d in bar:
            if p and lead is not None:
                inst(m, lead).notes.append(pm.Note(int(random.randint(78, 96) * lead_vel), N(p) + 12 * lead_oct, t(b), t(b + d) - .03))
            b += d
    b = 0
    for bar in chords:
        for root, q, d in bar:
            low = chord_notes(root, q, 3)
            tones = [low[0], low[2], low[0] + 12, low[1] + 12]
            add = lambda v, n, s, e: inst(m, comp).notes.append(pm.Note(v, n, s, e))
            if style == "arp":  # 8분 아르페지오
                for i in range(int(d * 2)):
                    add(random.randint(52, 66), tones[[0, 1, 2, 3, 2, 1, 2, 3][i % 8]], t(b + i / 2), t(b + i / 2 + .5) + .25)
            elif style == "strum":  # 우쿨렐레식 다운·업
                for o, v in [(0, 72), (1, 56), (1.5, 60), (2.5, 54), (3, 66), (3.5, 56)]:
                    if o < d:
                        for j, n in enumerate(tones[1:] + [low[2] + 12]):
                            add(v, n + 12, t(b + o) + j * .012, t(b + o) + j * .012 + .3)
            elif style == "waltz":  # 3/4 쿵-짝-짝: 1박 베이스(마디마다 근음·5음 번갈아), 2·3박 화음
                add(random.randint(70, 80), N(f"{root}2") + (7 if round((b + b0) / 3) % 2 else 0), t(b), t(b + 1) - .05)
                for i in (1, 2):
                    for n in low:
                        add(random.randint(48, 60), n + 12, t(b + i), t(b + i) + .22)
            elif style == "arp3":  # 3/4 8분 아르페지오 (하프)
                for i, idx in enumerate([0, 1, 2, 3, 2, 1][:int(d * 2)]):
                    add(random.randint(50, 64), tones[idx], t(b + i / 2), t(b + i / 2) + 1.2)
            if bass is not None:
                for o, n in [(0, N(f"{root}2")), (2, N(f"{root}2") + 7)]:
                    if o < d:
                        inst(m, bass).notes.append(pm.Note(80, n, t(b + o), t(b + o + 1.5)))
            b += d
    if drums:  # 셰이커 8분, 킥 1·3, 림 2·4
        for i in range(int(b * 2)):
            h = i / 2
            inst(m, 0, True).notes.append(pm.Note(random.randint(34, 48), 82, t(h), t(h) + .05))
            if h % 2 == 0:
                inst(m, 0, True).notes.append(pm.Note(64, 36, t(h), t(h) + .1))
            if h % 2 == 1:
                inst(m, 0, True).notes.append(pm.Note(46, 37, t(h), t(h) + .1))
    return b0 + b


def ring(m, at_beat, bpm, layers):
    """마지막 화음 길게: layers = [(악기, [음 이름])]"""
    s = at_beat * 60 / bpm
    for prog, names in layers:
        for n in names:
            inst(m, prog).notes.append(pm.Note(70, N(n), s, s + 3.5))


def render(m, name):
    mid, wav = HERE / f"{name}.mid", HERE / f"{name}.wav"
    m.write(str(mid))
    subprocess.run([FS, "-ni", "-q", "-g", "0.55", "-r", "44100", "-F", str(wav), SF2, str(mid)], check=True)
    with wave.open(str(wav)) as w:  # 들어 보기 좋게 RMS −20 dB (영상에선 make_video 가 다시 맞춤)
        prm, a = w.getparams(), np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    a *= min(10 ** (-20 / 20) / (np.sqrt((a ** 2).mean()) / 32768), .95 * 32768 / abs(a).max())  # 최고점은 0.95 아래
    with wave.open(str(wav), "wb") as w:
        w.setparams(prm)
        w.writeframes(np.clip(a, -32767, 32767).astype(np.int16).tobytes())
    print(mid.name, f"{m.get_end_time():.1f}초")


def pop_song(name, bpm, mel, chords, intro, lead, comp, style, bass, double, swing=0.0, passes=5, seed=1):
    """4/4: 전주(반주) → 본 8마디 × passes (짝수 번째는 double 악기가 옥타브 위 겹침) → 끝맺음 마디 → 마지막 화음"""
    m = pm.PrettyMIDI(initial_tempo=bpm)
    kw = dict(comp=comp, style=style, bass=bass, swing=swing, seed=seed)
    b = part(m, 0, bpm, chords=bars(intro, 4), drums=True, **kw)
    for i in range(passes):
        if i % 2:
            part(m, b, bpm, mel=mel[:8], lead=double, lead_oct=1, lead_vel=.55, seed=seed + 7)
        b = part(m, b, bpm, mel=mel[:8], chords=chords[:8], lead=lead, drums=True, **kw)
    b = part(m, b, bpm, mel=mel[8:], chords=chords[8:], lead=lead, **kw)
    root = chords[0][0][0]
    ring(m, b, bpm, [(comp, [f"{root}3", f"{root}4"]), (bass, [f"{root}2"])])
    render(m, name)


def musicbox_waltz():
    """오르골 왈츠: 전주 4 · A · A'(첼레스타 옥타브 겹침) · B(하프 더함) · A' · 끝 2 + 마지막 화음"""
    bpm = 140
    m = pm.PrettyMIDI(initial_tempo=bpm)
    w = dict(comp=45, style="waltz", seed=11)
    b = part(m, 0, bpm, chords=bars("G C D D", 3), **w)
    for sec, (mel, ch) in enumerate([(W_G, WC_G), (W_G, WC_G), (W_G_B, WC_G_B), (W_G, WC_G)]):
        if sec in (1, 3):
            part(m, b, bpm, mel=mel, lead=8, lead_oct=1, lead_vel=.62, seed=21)
        if sec == 2:
            part(m, b, bpm, chords=ch, comp=46, style="arp3", seed=31)
        b = part(m, b, bpm, mel=mel, chords=ch, lead=10, **w)
    b = part(m, b, bpm, chords=bars("C D", 3), **w)
    ring(m, b, bpm, [(45, ["G2", "D3", "G3", "B3"]), (10, ["G5", "B5"]), (46, ["G3", "D4", "G4", "B4"])])
    render(m, "musicbox_waltz")


# ── 4/4 장르 곡 (7화음 · 반주·베이스·드럼 패턴) ──
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "maj7": (0, 4, 7, 11), "m7": (0, 3, 7, 10), "7": (0, 4, 7, 10)}


def chord(sym):
    """"Bbmaj7" → ("Bb", (0, 4, 7, 11))"""
    root = sym[:2] if len(sym) > 1 and sym[1] in "#b" else sym[:1]
    return root, QUAL[sym[len(root):]]


COMP = {  # 한 화음 구간(박 off 부터 d 박)에 반주를 놓는 법 → [(박, 음들, 길이, 세기)]
    "bossa": lambda bar, off, d, v: [(o, v, .35, 60) for o in ((0, 1.5, 3) if bar % 2 == 0 else (1, 2.5)) if off <= o < off + d],
    "ep": lambda bar, off, d, v: [(off, v, d - .1, 58)] + ([(off + 2.5, v, 1.3, 40)] if d == 4 else []),
    "funk": lambda bar, off, d, v: [(off + s / 4, [n + 12 for n in v], .09, 72 if s % 4 == 0 else 50)
                                    for s in range(int(d * 4)) if (1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0)[(int(off * 4) + s) % 16]],
    "pulse": lambda bar, off, d, v: [(off + i / 2, [(v + [n + 12 for n in v])[(0, 2, 1, 3, 2, 4, 3, 5)[i % 8] % (2 * len(v))]], .45, 56 if i % 2 else 64)
                                     for i in range(int(d * 2))],
    "skank": lambda bar, off, d, v: [(off + o, v, .22, 62) for o in (.5, 1.5, 2.5, 3.5) if o < d],  # 엇박 화음 (칼립소·레게)
    "alberti": lambda bar, off, d, v: [(off + i / 2, [(v[0] - 12, v[-1], v[1], v[-1])[i % 4] + 12], .4, 58 if i % 4 == 0 else 48)
                                       for i in range(int(d * 2))],  # 낮음-높음-가운데-높음
}
BASS = {  # 근음 기준 (박, 반음, 길이)
    "root5": [(0, 0, 1.5), (2, 7, 1.5)],
    "funk": [(0, 0, .4), (.75, 0, .3), (1.5, 12, .4), (2.5, 7, .4), (3.25, 0, .3)],
    "lofi": [(0, 0, 1.2), (2.5, 0, .8), (3.5, 7, .4)],
    "calypso": [(0, 0, .8), (1.5, 7, .4), (2, 12, .8), (3.5, 7, .4)],
    "walk": [(0, 0, .9), (1, 7, .9), (2, 12, .9), (3, 7, .9)],
}
DRUMS = {  # 마디 하나 (박, GM 드럼 음, 세기)
    "bossa": lambda bar: [(h / 2, 70, 34 + 6 * (h % 2)) for h in range(8)] + [(0, 36, 48), (2, 36, 44)]
                         + [(o, 37, 50) for o in ((0, 1.5, 3) if bar % 2 == 0 else (1, 2))],
    "lofi": lambda bar: [(0, 36, 72), (2.5, 36, 60), (1, 38, 56), (3, 38, 56)] + [(h / 2, 42, 32 + 10 * (h % 2 == 0)) for h in range(8)],
    "funk": lambda bar: [(0, 36, 74), (.75, 36, 56), (2.5, 36, 66), (1, 38, 70), (3, 38, 70)] + [(s / 4, 42, 50 if s % 2 == 0 else 30) for s in range(16)],
    "pulse": lambda bar: [(b, 36, 46) for b in range(4)] + [(b + .5, 46, 32) for b in range(4)] + [(1, 39, 36), (3, 39, 36)],
    "chip": lambda bar: [(0, 36, 70), (2, 36, 70), (1, 38, 60), (3, 38, 60)] + [(h / 2, 42, 40) for h in range(8)],
    "calypso": lambda bar: [(0, 36, 60), (2, 36, 60), (1.5, 64, 50), (3.5, 64, 50), (2.75, 63, 45)] + [(h / 2, 70, 40 if h % 2 else 30) for h in range(8)],
}


def groove(name, bpm, mel, end_mel, prog, intro, target, lead, comp, style, bass, bass_style, drums,
           double=None, pad=None, swing=0.0, seed=1):
    """전주 → 8마디 × (target 초를 넘을 만큼) → 끝 마디 → 마지막 화음. 짝수 번째 돌 때 double 이 옥타브 위 겹침.
    prog·intro = "Dmaj7 Em7,A7 …" (빈칸 = 마디, 쉼표 = 마디 반씩)"""
    random.seed(seed)
    beat, bar_s = 60 / bpm, 240 / bpm
    t = lambda b: (b + (swing if (b * 2) % 2 == 1 else 0)) * beat + random.uniform(-.008, .008)
    note = lambda prog_, vel, n, s, e: inst(m, prog_).notes.append(pm.Note(max(1, min(127, vel + random.randint(-6, 6))), n, t(s), t(e)))
    m = pm.PrettyMIDI(initial_tempo=bpm)
    body, intro = [b.split(",") for b in prog.split()], [b.split(",") for b in intro.split()]
    passes = max(1, -(-(target - (len(intro) + 1) * bar_s - 2.5) // (8 * bar_s)))  # 끝 화음 울림까지 target 을 넘는 최소
    plan = [(c, None, 0) for c in intro]
    for p in range(int(passes)):
        plan += [(c, mel[i], p) for i, c in enumerate(body)]
    plan.append(([body[0][0]], end_mel, -1))
    for bi, (chs, ml, p) in enumerate(plan):
        B = bi * 4
        d = 4 / len(chs)
        for ci, sym in enumerate(chs):
            root, ivs = chord(sym)
            tones = [N(f"{root}3") + i for i in ivs]
            voic = tones[1:] + [tones[0] + 12]
            if p == -1:  # 끝 마디는 한 번 치고 울림
                note(comp, 60, tones[0] + 12, B, B + 4)
                continue
            for o, ns, ln, vel in COMP[style](bi, ci * d, d, voic):
                for n in (ns if isinstance(ns, list) else [ns]):
                    note(comp, vel, n, B + o, B + o + ln)
            if pad is not None:
                for n in voic:
                    note(pad, 42, n + 12, B + ci * d, B + ci * d + d)
            for o, semi, ln in BASS[bass_style]:
                if ci * d <= o < ci * d + d:
                    note(bass, 78, N(f"{root}2") + semi, B + o, B + o + ln)
        if p != -1 and drums:
            for o, dn, vel in DRUMS[drums](bi):
                inst(m, 0, True).notes.append(pm.Note(max(1, vel + random.randint(-5, 5)), dn, t(B + o), t(B + o) + .1))
        if ml:
            b = B
            for pn, dur in ml:
                if pn:
                    note(lead, random.randint(80, 94), N(pn), b, b + dur - .05)
                    if double is not None and p % 2 == 1:
                        note(double, 52, N(pn) + 12, b, b + dur - .05)
                b += dur
    end = len(plan) * 4 * beat
    root, ivs = chord(body[0][0])
    for prog_, ns in [(comp, [N(f"{root}3") + i for i in ivs]), (bass, [N(f"{root}2")])] + ([(pad, [N(f"{root}4") + i for i in ivs])] if pad is not None else []):
        for n in ns:
            inst(m, prog_).notes.append(pm.Note(64, n, end - 4 * beat, end + 2.5))
    render(m, name)


# 바플(구매관리): 보사노바 — 플루트 + 나일론 기타 + 브러시 느낌 퍼커션, D장조
BOSSA = [[("F#5", 1.5), ("E5", .5), ("F#5", 1), ("A5", 1)], [("G5", 1.5), ("F#5", .5), ("E5", 2)],
         [("C#6", 1), ("A5", .5), ("F#5", .5), ("E5", 1), ("C#5", 1)], [("D5", 1.5), ("F#5", .5), ("B5", 2)],
         [("B5", 1), ("A5", .5), ("G5", .5), ("F#5", 1), ("D5", 1)], [("E5", 1.5), ("G5", .5), ("C#6", 1), ("B5", 1)],
         [("A5", 3), (None, 1)], [("C#5", .5), ("E5", .5), ("G5", .5), ("B5", .5), ("A5", 2)]]
# 업무 자동화: 로파이 — 일렉 피아노 7화음 + 비브라폰 + 스윙, F장조
LOFI = [[("A5", 1.5), ("G5", .5), ("E5", 1), ("C5", 1)], [("D5", .5), ("E5", .5), ("G5", 1), ("E5", 1), (None, 1)],
        [("F5", 1), ("A5", 1), ("C6", 1.5), ("A5", .5)], [("A#5", 1), ("A5", .5), ("G5", .5), ("E5", 2)],
        [("C5", .5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5), ("E5", 1)], [("D5", 1.5), ("F5", .5), ("A5", 2)],
        [("A#5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("D5", 2)], [("E5", 1), ("G5", 1), ("A#5", 1), (None, 1)]]
# 엑셀 정리기: 가벼운 펑크 — 뮤트 기타 16분 + 통통 베이스 + 피아노 스타카토, A단조
FUNK = [[("E5", .5), ("G5", .5), ("A5", .5), (None, .5), ("C6", .5), ("A5", .5), ("G5", 1)],
        [("F#5", .5), ("A5", .5), (None, .5), ("F#5", .5), ("E5", 1), ("D5", 1)],
        [("C5", .5), ("F5", .5), ("A5", .5), ("C6", .5), ("E6", 1), ("C6", 1)],
        [("B5", .5), ("G#5", .5), ("E5", 1), ("D5", .5), ("E5", .5), (None, 1)],
        [("A5", .5), ("C6", .5), ("E6", .5), (None, .5), ("D6", .5), ("C6", .5), ("A5", 1)],
        [("F#5", 1), ("A5", .5), ("C6", .5), ("B5", 1), ("A5", 1)],
        [("A5", .5), ("G5", .5), ("F5", 1), ("G#5", 1), ("B5", 1)], [("A5", 2), (None, 2)]]
# 도면 검색기: 미니멀 펄스 — 피아노 8분 아르페지오 + 현악 패드 + 칼림바, E단조
PULSE = [[("B4", 1), ("E5", 1), ("G5", 1), ("F#5", 1)], [("E5", 2), ("G5", 1), ("C6", 1)],
         [("B5", 1.5), ("A5", .5), ("G5", 1), ("D5", 1)], [("F#5", 3), (None, 1)],
         [("G5", 1), ("B5", 1), ("E6", 1), ("D6", 1)], [("C6", 1.5), ("B5", .5), ("G5", 2)],
         [("A5", 1), ("F#5", 1), ("D5", 1), ("F#5", 1)], [("A5", 3), (None, 1)]]

# 다운로드 자동 정리: 8비트 팝 — 스퀘어 리드·아르페지오 + 신스 베이스, G장조
CHIP = [[("D5", .5), ("G5", .5), ("B5", .5), ("G5", .5), ("D6", 1), ("B5", 1)], [("A5", .5), ("F#5", .5), ("D5", .5), ("F#5", .5), ("A5", 2)],
        [("G5", .5), ("E5", .5), ("B4", .5), ("E5", .5), ("G5", 1), ("B5", 1)], [("C6", 1), ("B5", .5), ("A5", .5), ("G5", 1), ("E5", 1)],
        [("B5", .5), ("D6", .5), ("G6", .5), ("D6", .5), ("B5", 1), ("G5", 1)], [("F#5", .5), ("A5", .5), ("D6", .5), ("A5", .5), ("F#5", 2)],
        [("E5", .5), ("G5", .5), ("C6", .5), ("E6", .5), ("D6", 1), ("C6", 1)], [("B5", 1), ("A5", 1), ("F#5", 1), (None, 1)]]
# 수입 서류 점검: 칼립소 — 스틸드럼 + 엇박 기타 + 콩가·마라카스, C장조
CALYPSO = [[("E5", .5), ("G5", .5), (None, .5), ("C6", .5), (None, .5), ("G5", .5), ("E5", 1)],
           [("F5", .5), ("A5", .5), (None, .5), ("C6", .5), ("A5", 1), ("F5", 1)],
           [("G5", .5), ("B5", .5), ("D6", .5), ("B5", .5), ("G5", 1), ("D5", 1)], [("E5", 1.5), ("D5", .5), ("C5", 2)],
           [("A5", .5), ("C6", .5), ("E6", .5), ("C6", .5), ("A5", 1), ("E5", 1)], [("F5", .5), ("A5", .5), ("C6", 1), ("D6", .5), ("C6", .5), ("A5", 1)],
           [("B5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("E5", 1), ("D5", 1)], [("G5", 2), (None, 2)]]
# 장비 대장·제출 서류: 가벼운 바로크 — 하프시코드 알베르티 + 오보에 + 현악 패드, D장조
BAROQUE = [[("F#5", 1), ("E5", .5), ("D5", .5), ("E5", 1), ("F#5", 1)], [("E5", 1), ("C#5", .5), ("A4", .5), ("C#5", 1), ("E5", 1)],
           [("D5", 1), ("F#5", .5), ("B5", .5), ("A5", 1), ("F#5", 1)], [("C#5", 1.5), ("D5", .5), ("E5", 2)],
           [("D5", .5), ("E5", .5), ("G5", .5), ("B5", .5), ("D6", 1), ("B5", 1)], [("A5", 1), ("F#5", .5), ("A5", .5), ("D6", 2)],
           [("B5", 1), ("A5", .5), ("G5", .5), ("F#5", 1), ("E5", 1)], [("E5", 2), ("C#5", 1), (None, 1)]]

SONGS = {
    # 우쿨렐레: 휘파람(GM 은 혼처럼 들림) + 나일론 스트럼 + 베이스 + 셰이커, 짝수 번째에 글로켄슈필 겹침
    "uke_whistle": lambda: pop_song("uke_whistle", 112, MEL_C, CH_C, "C G", lead=78, comp=24, style="strum", bass=32, double=9, seed=1),
    # 마림바: 휘파람 + 마림바 아르페지오 + 베이스, 셔플, 짝수 번째에 비브라폰 겹침
    "marimba_shuffle": lambda: pop_song("marimba_shuffle", 100, MEL_F, CH_F, "F C", lead=78, comp=12, style="arp", bass=32, double=11, swing=.16, seed=3),
    "musicbox_waltz": musicbox_waltz,
    "bossa_flute": lambda: groove("bossa_flute", 124, BOSSA, [("D6", 3), (None, 1)], "Dmaj7 Em7 F#m7 Bm7 Gmaj7 A7 Dmaj7 A7", "Dmaj7 A7",
                                  target=38.1, lead=73, comp=24, style="bossa", bass=32, bass_style="root5", drums="bossa", double=9, seed=41),
    "lofi_keys": lambda: groove("lofi_keys", 84, LOFI, [("A5", 3), (None, 1)], "Fmaj7 Em7,A7 Dm7 Gm7,C7 Fmaj7 Bbmaj7 Gm7 C7", "Fmaj7 C7",
                                target=50.6, lead=11, comp=4, style="ep", bass=33, bass_style="lofi", drums="lofi", swing=.18, seed=42),
    "funk_clean": lambda: groove("funk_clean", 104, FUNK, [("C6", .5), ("B5", .5), ("A5", 3)], "Am7 D7 Fmaj7 E7 Am7 D7 Fmaj7,E7 Am7", "Am7 E7",
                                 target=51.4, lead=0, comp=28, style="funk", bass=33, bass_style="funk", drums="funk", double=11, seed=43),
    "pulse_kalimba": lambda: groove("pulse_kalimba", 112, PULSE, [("E5", 4)], "Em C G D Em C D D", "Em C",
                                    target=51.0, lead=108, comp=0, style="pulse", bass=33, bass_style="root5", drums="pulse", pad=49, seed=44),
    "chip_tidy": lambda: groove("chip_tidy", 132, CHIP, [("G5", .5), ("B5", .5), ("D6", 3)], "G D Em C G D C D", "G C D",
                                target=37.8, lead=80, comp=80, style="pulse", bass=38, bass_style="root5", drums="chip", seed=45),
    "calypso_steel": lambda: groove("calypso_steel", 116, CALYPSO, [("E5", .5), ("G5", .5), ("C6", 3)], "C F G C Am F G G", "C G",
                                    target=41.1, lead=114, comp=25, style="skank", bass=32, bass_style="calypso", drums="calypso", double=12, seed=46),
    "baroque_oboe": lambda: groove("baroque_oboe", 108, BAROQUE, [("F#5", .5), ("E5", .5), ("D5", 3)], "D A Bm F#m G D G A", "D A",
                                   target=41.6, lead=68, comp=6, style="alberti", bass=45, bass_style="walk", drums=None, pad=48, seed=47),
}

if __name__ == "__main__":
    import sys
    for name in sys.argv[1:] or SONGS:
        SONGS[name]()

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
    a *= 10 ** (-20 / 20) / (np.sqrt((a ** 2).mean()) / 32768)
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


# 우쿨렐레: 휘파람(GM 은 혼처럼 들림) + 나일론 스트럼 + 베이스 + 셰이커, 짝수 번째에 글로켄슈필 겹침
pop_song("uke_whistle", 112, MEL_C, CH_C, "C G", lead=78, comp=24, style="strum", bass=32, double=9, seed=1)
# 마림바: 휘파람 + 마림바 아르페지오 + 베이스, 셔플, 짝수 번째에 비브라폰 겹침
pop_song("marimba_shuffle", 100, MEL_F, CH_F, "F C", lead=78, comp=12, style="arp", bass=32, double=11, swing=.16, seed=3)

# 오르골 왈츠: 전주 4 · A · A'(첼레스타 옥타브 겹침) · B(하프 더함) · A' · 끝 2 + 마지막 화음
BPM = 140
m = pm.PrettyMIDI(initial_tempo=BPM)
w = dict(comp=45, style="waltz", seed=11)
b = part(m, 0, BPM, chords=bars("G C D D", 3), **w)
for sec, (mel, ch) in enumerate([(W_G, WC_G), (W_G, WC_G), (W_G_B, WC_G_B), (W_G, WC_G)]):
    if sec in (1, 3):
        part(m, b, BPM, mel=mel, lead=8, lead_oct=1, lead_vel=.62, seed=21)
    if sec == 2:
        part(m, b, BPM, chords=ch, comp=46, style="arp3", seed=31)
    b = part(m, b, BPM, mel=mel, chords=ch, lead=10, **w)
b = part(m, b, BPM, chords=bars("C D", 3), **w)
ring(m, b, BPM, [(45, ["G2", "D3", "G3", "B3"]), (10, ["G5", "B5"]), (46, ["G3", "D4", "G4", "B4"])])
render(m, "musicbox_waltz")

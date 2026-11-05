"""ocr 영상 배경음: 비제 「하바네라」 1–19마디를 첼로 4대로 직접 편곡한다.

출처: Bizet, Carmen, 보컬 스코어(성악 + 피아노), Paris: Choudens.
  https://archive.org/details/carmenopracomi00bize (1883, PDF 57–58쪽)
  https://archive.org/details/carmenopraen4act00bize (1900, 찢어진 12마디를 여기서 읽음, PDF 53–54쪽)
파트 1 = 카르멘의 노래, 파트 2·3 = 피아노 오른손 화음, 파트 4 = 왼손. 전부 한 옥타브 내림(파트 4 빼고).
빠르기: 악보 ♩=72 → 58. 19마디 안에서 영상이 끝난다(곡 끝 40.3초, 영상 39.2초).

실행: python ocr/make_bgm.py  ->  music/habanera_quartet.mid (커밋 안 함)
영상: python make_video.py ocr --sfx --sfx-db -10 --bgm music/habanera_quartet.mid
"""
from pathlib import Path

import mido

OUT = Path(__file__).parent.parent / "music" / "habanera_quartet.mid"
TPB, BAR = 480, 960  # 2/4
LEAD = 480  # 앞 한 박 비움: 표지 길이(make_video.py)와 맞음
BPM = 58
CELLO, PIZZ = 42, 45  # GM 악기
PITCH = {n: i for i, n in enumerate("C C# D Eb E F F# G G# A Bb B".split())}


def p(name):
    return 12 * (int(name[-1]) + 1) + PITCH[name[:-1]]


# 노래 (시작 틱, 길이, 음). 악보 음높이 그대로 적고 아래에서 옥타브 내림
PICKUP = [(480, 240, "D5"), (720, 240, "C#5")]
RUN = [(0, 160, "C5"), (160, 160, "C5"), (320, 160, "C5"), (480, 240, "B4"), (720, 240, "Bb4")]
TURN1 = [(0, 80, "F4"), (80, 80, "G4"), (160, 80, "F4"), (240, 120, "E4"), (360, 120, "F4"), (480, 240, "G4"), (720, 240, "F4")]
TURN2 = [(0, 80, "E4"), (80, 80, "F4"), (160, 80, "E4"), (240, 120, "D4"), (360, 120, "E4"), (480, 240, "F4"), (720, 240, "E4")]


def fall(last1, last2, gap):  # A A (쉼) A + 8분음표 둘. gap=True 면 16분쉼이 있는 꼴
    a = [(0, 120, "A4"), (120, 120, "A4"), (360, 120, "A4")] if gap else [(0, 240, "A4"), (240, 120, "A4"), (360, 120, "A4")]
    return a + [(480, 240, last1), (720, 240, last2)]


VOICE = {4: PICKUP, 5: RUN, 6: fall("G#4", "G4", False), 7: TURN1, 8: [(0, 240, "E4")] + PICKUP,
         9: RUN, 10: fall("G4", "F4", True), 11: TURN2, 12: [(0, 480, "D4")] + PICKUP,
         13: RUN, 14: fall("G#4", "G4", True), 15: TURN1, 16: [(0, 480, "E4")] + PICKUP,
         17: RUN, 18: fall("G4", "F4", True), 19: TURN2}

# 오른손 화음에서 맨 윗음(노래와 같음)을 뺀 나머지. 마디 → [틱 0, 틱 480, 틱 720]
DF, ED, DA, DB, CG = ("F4", "D4"), ("E4", "D4"), ("D4", "A3"), ("D4", "Bb3"), ("C#4", "G3")
HOLD = (None, None)
CHORDS = {4: [HOLD, DF, DF], 5: [DF, DF, DF], 6: [DF, DA, DA], 7: [DA, DA, DA], 8: [DB, ED, ED],
          9: [ED, ED, ED], 10: [ED, DB, DB], 11: [CG, ("C#4", None), CG], 12: [("D4", "F3"), DF, DF],
          13: [DF, DF, DF], 14: [DF, DA, DA], 15: [DA, DA, DA], 16: [DB, ED, ED],
          17: [ED, ED, ED], 18: [ED, DB, DB], 19: [CG, ("C#4", None), CG]}

# 왼손 "D · A F A": 마디별 (둘째 음, 셋째 음)
BASS_F, BASS_G, BASS_AG = ("A2", "F3"), ("Bb2", "G3"), ("A2", "G3")
BASS = {b: BASS_F for b in range(1, 20)} | {b: BASS_G for b in (8, 9, 10, 16, 17, 18)} | {11: BASS_AG, 19: BASS_AG}

# 파트별 (악기, CC7, 세기). 옛 판에서 귀로 맞춘 음량. 파트 4 는 도입 뒤 멜로디 밑으로 물러남
PARTS = [(CELLO, 105, 59), (PIZZ, 110, 40), (PIZZ, 110, 40), (PIZZ, 110, 58)]
BASS_AFTER_INTRO = 34  # 멜로디 대 반주 음량 차를 옛 판(−1.7 dB)에 맞춘 값
INTRO_BARS = 4


def build():
    """파트마다 (시작 틱, 길이, 음, 세기) 목록. 마디 번호는 악보와 같음."""
    parts = [[] for _ in PARTS]
    at = lambda bar, tick: (bar - 1) * BAR + tick
    for bar, notes in VOICE.items():
        parts[0] += [(at(bar, t), n - 1, p(x) - 12, PARTS[0][2]) for t, n, x in notes]
    for bar, chords in CHORDS.items():
        for tick, (hi, lo) in zip((0, 480, 720), chords):
            for k, x in ((1, hi), (2, lo)):
                if x:
                    parts[k].append((at(bar, tick), 239, p(x) - 12, PARTS[k][2]))
    for bar, (second, third) in BASS.items():
        v = PARTS[3][2] if bar <= INTRO_BARS else BASS_AFTER_INTRO
        parts[3] += [(at(bar, t), n, p(x), v) for t, n, x in
                     ((0, 197, "D2"), (360, 100, second), (480, 197, third), (720, 197, second))]
        if bar <= INTRO_BARS:  # 폰 스피커에 D2 가 안 들려 도입만 윗옥타브를 겹침
            parts[2].append((at(bar, 0), 197, p("D3"), 54))
    return parts


def write(parts):
    m = mido.MidiFile(ticks_per_beat=TPB)
    for ch, (notes, (program, volume, _)) in enumerate(zip(parts, PARTS)):
        t = mido.MidiTrack()
        m.tracks.append(t)
        head = [mido.Message("program_change", channel=ch, program=program),
                mido.Message("control_change", channel=ch, control=7, value=volume),
                mido.Message("control_change", channel=ch, control=91, value=0),  # 잔향 없이
                mido.Message("control_change", channel=ch, control=93, value=0)]
        if ch == 0:
            head.insert(0, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
        t.extend(head)
        events = []
        for start, length, note, vel in notes:
            events.append((start + LEAD, 1, note, vel))
            events.append((start + LEAD + length, 0, note, 0))
        last = 0
        for tick, _, note, vel in sorted(events):
            t.append(mido.Message("note_on", channel=ch, note=note, velocity=vel, time=tick - last))
            last = tick
    return m


def check(parts):
    assert len(parts) == 4
    for notes in parts:
        assert min(n for _, _, n, _ in notes) >= p("C2"), "첼로 최저음 아래"
    for bar, notes in VOICE.items():  # 노래: 겹침 없이 마디 안에
        end = 0
        for t, n, _ in notes:
            assert t >= end and t + n <= BAR, (bar, t)
            end = t + n
    assert sorted(VOICE) == list(range(4, 20)) and sorted(CHORDS) == list(range(4, 20)) and sorted(BASS) == list(range(1, 20))


if __name__ == "__main__":
    parts = build()
    check(parts)
    write(parts).save(OUT)
    print(OUT, "저장,", sum(map(len, parts)), "음")

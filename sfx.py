"""데모 영상 효과음: numpy 로 합성한 짧은 소리(음원 파일·저작권 없음)를 시각 목록대로 깐다.

make_video.py --sfx 가 쓴다. 소리 이름은 demo.js 의 SFX 표·data-sfx 에 적는 이름과 같다.
"""
import numpy as np

SR = 48000


def _t(d):
    return np.arange(int(SR * d)) / SR


def _tone(f, d, decay, vol):
    return vol * np.sin(2 * np.pi * f * _t(d)) * np.exp(-_t(d) / decay)


def _sweep(f0, f1, d):
    return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, int(SR * d))) / SR)


def _noise(d, smooth=1):
    n = np.random.default_rng(7).standard_normal(int(SR * d))
    return np.convolve(n, np.ones(smooth) / smooth, "same") if smooth > 1 else n


SOUNDS = {
    "click": 0.45 * _noise(0.03) * np.exp(-_t(0.03) / 0.003) + _tone(3200, 0.03, 0.005, 0.25),  # 마우스 딸깍
    "menu": 0.18 * _sweep(900, 1500, 0.07) * np.exp(-_t(0.07) / 0.03),  # 작은 팝(메뉴·알림)
    "pop": 0.32 * _sweep(450, 1100, 0.12) * np.exp(-_t(0.12) / 0.045),  # 카드·칩이 튀어나옴
    "tick": _tone(1760, 0.09, 0.03, 0.22) + _tone(2640, 0.09, 0.02, 0.1),  # 완료 ✓
    "roll": _tone(2200, 0.04, 0.012, 0.07),  # 연달아 채워지는 칸
    "buzz": 0.16 * np.sign(np.sin(2 * np.pi * 160 * _t(0.16))) * np.exp(-_t(0.16) / 0.08),  # 틀림 ✗
    "swish": 0.5 * (_noise(0.2, 24) - _noise(0.2, 96)) * np.sin(np.pi * _t(0.2) / 0.2) ** 2,  # 선 긋기
    "chime": sum(_tone(f, 0.8, 0.25, v) for f, v in ((880, 0.16), (1320, 0.12), (1760, 0.07))),  # 다 됨
    "whoosh": 1.2 * _noise(0.35, 60) * np.sin(np.pi * _t(0.35) / 0.35) ** 3,  # 장면 넘김
}


def pluck(midi, dur=1.4, decay=0.996, ring=0.9):
    """Karplus-Strong: 잡음 한 주기를 평균 내며 되풀이 → 줄 뜯는 소리. 한 주기씩 묶어 numpy 로."""
    p = max(2, round(SR / (440 * 2 ** ((midi - 69) / 12))))
    n = int(SR * dur)
    y = np.zeros(n + 2 * p)
    w = max(3, p // 6)  # 첫 뜯김을 주기의 1/6 창으로 부드럽게 → 쨍한 철줄 대신 나일론 쪽
    exc = np.random.default_rng(midi).uniform(-1, 1, p + 2 * w)
    y[:p] = np.convolve(exc, np.ones(w) / w, "same")[w:p + w]
    for k in range(p, n + p, p):
        prev = y[k - p:k]
        y[k:k + p] = decay * 0.5 * (prev + np.concatenate(([y[k - p - 1] if k > p else 0], prev[:-1])))
    return y[:n] * np.exp(-np.arange(n) / (SR * ring))


# 배경 반주. 보이싱은 표준 조율 기타 코드(MIDI)
G, D, EM, C = (43, 47, 50, 55, 59, 67), (50, 57, 62, 66), (40, 47, 52, 55, 59, 64), (48, 52, 55, 60, 64)


def _arp(seconds):
    """G–D–Em–C 아르페지오, 100 BPM 8분음표 → [(초, MIDI, 세기, 소리 길이)]"""
    eighth, pat = 60 / 100 / 2, (0, 2, 3, 4, 5, 4, 3, 2)
    for i in range(int(seconds / eighth) + 1):
        chord = (G, D, EM, C)[i // len(pat) % 4]
        yield i * eighth, chord[pat[i % len(pat)] % len(chord)], 1.0 if i % len(pat) == 0 else 0.7, 0.9


def _waltz(seconds):
    """3/4 쿵-짝-짝, 168 BPM. G–Em–C–D 두 마디씩, 둘째 마디 베이스는 5음. 짝은 위 세 줄을 12ms 간격으로 긁음"""
    beat = 60 / 168
    for bar in range(int(seconds / (3 * beat)) + 1):
        chord, t = (G, EM, C, D)[bar // 2 % 4], bar * 3 * beat
        root = chord[0]
        yield t, root if bar % 2 == 0 else (root + 7 if root + 7 <= 50 else root - 5), 1.0, 0.9
        for b in (1, 2):
            for j, note in enumerate(chord[-3:]):
                yield t + b * beat + 0.012 * j, note, 0.28, 0.35


STYLES = {"arp": _arp, "waltz": _waltz}


def bgm(seconds, style="waltz"):
    n = int(SR * seconds)
    out = np.zeros(n + 2 * SR)
    cache = {}
    for t, note, vel, ring in STYLES[style](seconds):
        s = cache.setdefault((note, ring), pluck(note, ring=ring))
        k = int(SR * t)
        out[k:k + len(s)] += s * vel
    return out[:n]


def _bed(m, n):
    """배경음을 n 샘플로 자르고(모자라면 무음) 앞 1초·뒤 2초 페이드, RMS 를 −25 dBFS 로"""
    m = np.pad(m[:n], (0, max(0, n - len(m))))
    fi, fo = min(n, SR), min(n, 2 * SR)
    m[:fi] *= np.linspace(0, 1, fi)
    m[n - fo:] *= np.linspace(1, 0, fo)
    rms = np.sqrt((m ** 2).mean())
    return m * (10 ** (-25 / 20) / rms) if rms > 0 else m


def mix(events, seconds, frame=1024, music=None):
    """events = [(초, 소리 이름)] → (2, n) float32 스테레오. 길이는 frame 의 배수(AAC 프레임)로 맞춘다.
    music="waltz"·"arp" 면 그 합성 기타 반주를, 1차원 배열(SR, 모노)이면 그 음악을 효과음(최고 0.8) 밑에 RMS −25 dBFS 로 깐다."""
    n = -(-int(SR * seconds) // frame) * frame
    out = np.zeros(n + SR)
    for t, name in events:
        s = SOUNDS[name]
        k = max(0, int(SR * t))
        out[k:k + len(s)] += s[: len(out) - k]
    out = out[:n]
    peak = np.abs(out).max()
    if peak > 0:
        out *= 0.8 / peak
    if music is not None:
        out += _bed(bgm(n / SR, music) if isinstance(music, str) else np.asarray(music, dtype=float), n)
        out /= max(1.0, np.abs(out).max() / 0.95)
    return np.repeat(out[None, :], 2, axis=0).astype(np.float32)


if __name__ == "__main__":
    a = mix([(0.1, "click"), (0.5, "pop"), (1.9, "chime")], 3)
    assert a.shape[0] == 2 and a.shape[1] % 1024 == 0 and a.shape[1] >= 3 * SR
    assert abs(np.abs(a).max() - 0.8) < 1e-6 and not a[:, : int(0.1 * SR) - 1].any()
    # 뜯은 줄의 주기가 음높이와 맞는지 (A2 = 110 Hz): 자기상관이 가장 큰 지연 = 한 주기
    s = pluck(45)[: SR // 2]
    ac = np.correlate(s, s, "full")[len(s) - 1:]
    lo, hi = SR // 400, SR // 60
    f = SR / (lo + np.argmax(ac[lo:hi]))
    assert abs(f - 110) < 2, f
    for music in (*STYLES, np.sin(np.arange(2 * SR) / SR * 2 * np.pi * 220)):  # 받은 음악이 영상보다 짧은 경우까지
        b = mix([], 5, music=music)
        assert b.shape[1] >= 5 * SR and 0 < np.abs(b).max() <= 0.95
    print("ok", a.shape, f"pluck A2 {f} Hz")

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


def mix(events, seconds, frame=1024):
    """events = [(초, 소리 이름)] → (2, n) float32 스테레오. 길이는 frame 의 배수(AAC 프레임)로 맞춘다."""
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
    return np.repeat(out[None, :], 2, axis=0).astype(np.float32)


if __name__ == "__main__":
    a = mix([(0.1, "click"), (0.5, "pop"), (1.9, "chime")], 3)
    assert a.shape[0] == 2 and a.shape[1] % 1024 == 0 and a.shape[1] >= 3 * SR
    assert abs(np.abs(a).max() - 0.8) < 1e-6 and not a[:, : int(0.1 * SR) - 1].any()
    print("ok", a.shape)

# OMR 데모의 자료와 검증 범위

2026-11-10 재구성. 본편 4장면과 접힌 부록 2개로 구성한다.

## 공개 시연 자료

- 하바네라 1883년 Choudens 판 스캔: 기존 `habanera_bars5-8.jpg`. 공개 시연을 위해 사용한 자료이며 왈츠 성능 측정 입력과 다르다.
- 사진 효과: `render_bars.py`의 설명용 처리. 실제 휴대폰 촬영본으로 소개하지 않는다.
- 실제 판독: `habanera_omr.mxl`의 P10, 7마디. 첫 음 F4를 G4로 바꾼 두 MusicXML 파일과 SVG를 `build_demo_assets.py`로 만든다. 음높이 하나 외의 음악 데이터가 동일한지 생성 중 검사한다.
- 보정 설명: 같은 판독 결과에 누락된 마지막 F4 하나만 직접 추가한다. 실제 자동 보정 결과가 아니며 다른 리듬·표기 오류는 남아 있다. 이전의 슬러·스타카토·셈여림 추가 그림은 새 데모에서 사용하지 않는다.
- 부록의 음높이 비교는 두 파일의 첫 음(65/67 MIDI)에 대응하는 합성음이다. MuseScore 조작 화면이나 첼로 녹음으로 소개하지 않는다. 수정 전후 MusicXML 다운로드가 가능하다.

## 선택 규칙 확인

비공개 `score-ocr` 저장소의 `7795793`에서 `pick.py`를 읽어 확인했다. 원본 사진·편곡 악보·비공개 코드는 이 저장소로 복사하지 않았다.

1. 시스템별 마디 수를 맞춰 비교할 수 있는 후보를 고른다.
2. 마디의 음 길이가 목표 박자에 맞는 후보를 우선한다.
3. 음높이/쉼표·길이·화음 여부 서명의 일치 수, 같은 음 서명 내 붙임줄 패턴의 일치 수, 입력 순서 순으로 선택한다.
4. 길이가 맞는 후보가 없으면 남은 후보 중 선택하고 해당 마디를 로그에 남긴다. 다수의 판독이 같은 오류를 낼 수 있다.

본편 3장면은 3개 후보를 이용한 설명용 도식이다. 빨강/초록으로 정답을 미리 알고 고르는 것처럼 표현하지 않는다. 간단한 예제에서 실제 `pick()`으로 길이 우선과 후보 일치 선택을 확인한다. 여섯 썸네일은 명암 변형 예시이지 이번에 여섯 번 인식한 증거가 아니다.

## 36 → 5의 의미

같은 저장소의 README 기록 및 `regress.py` 비교 범위를 확인했다.

- 왈츠 사진 A: 첼로 파트 사진 3장, 정답 악보 219마디. 2026-10-25 개발 기록과 10-27 재현 기록.
- 비교 대상: 음높이·길이·붙임줄. 슬러·셈여림 등 연주 표시는 제외한다.
- 남은 5마디: 여러 마디 쉼표 구간 m144–147와 잘못 읽은 붙임줄 m183.
- 이번 데모 작업에서 원본 사진으로 Audiveris 전체 인식을 다시 실행한 것은 아니다. 중간 수치 34·15·9는 본편에서 생략했다.

## 다시 만들기

```text
python ocr/build_demo_assets.py
python render_cards.py ocr
python fx_check.py ocr.html
python make_video.py ocr --sfx --sfx-db -10 --bgm music/habanera_quartet.wav
python build_site.py
```

SVG 생성은 [Verovio 6.0.0 브라우저판](https://www.verovio.org/javascript/6.0.0/verovio-toolkit-wasm.js)을 빌드 때만 사용한다. 배포 페이지에는 생성된 SVG와 MusicXML만 포함한다. 브라우저용 생성 방식은 Windows 네이티브 DLL 설치가 필요 없다.

반주는 기존 `make_bgm.py`의 4파트·음표·템포·음량을 유지한다. 길이가 더 필요하면 마지막 8마디(12–19)를 반복하고 영상 끝에서 페이드한다. 이번 렌더는 [js-synthesizer 1.11.0](https://github.com/jet2jet/js-synthesizer) / FluidSynth 2.4.6 WASM과 [MuseScore 4.4.4의 FluidR3Mono_GM.sf3](https://github.com/musescore/MuseScore/blob/v4.4.4/share/sound/FluidR3Mono_GM.sf3)를 사용했다. 이전 PC의 FluidR3 GM SF2와 악기 렌더링이 완전히 동일하다고 보장하지 않는다.

```text
python ocr/bgm_events.py events.json --seconds 52
node ocr/render_bgm.cjs <js-synthesizer 폴더> <FluidR3Mono_GM.sf3> events.json music/habanera_quartet.wav
```

음원 원본·SoundFont·설치 패키지는 공개 저장소에 포함하지 않는다. 오디오 트랙·음높이·피크 검사는 실제 청취 평가와 구분해서 보고한다.

## 이번 산출물 확인

- 카드 4장, 표지 포함 MP4 45.1초 / 1353프레임 / 1080×1920 / 30fps.
- 웹 재생과 영상 시계 대조 4장면 통과. 각 장면 끝과 카드·인코딩된 MP4를 대조했다.
- 1440·390·320px 화면, 모바일 다크 모드, 부록 키보드 조작, 다운로드 파일 선택, 녹화 모드 숨김 확인.
- 브라우저 음높이 F4/G4 및 최종 MP4의 음 시작 구간 349/392Hz 확인. MP4 오디오 피크 약 0.294, 클리핑 없음.
- 사이트 내부 파일 연결 130개 확인. 별도 관람자 이해 평가와 음색·밸런스 청취 평가는 미실시.

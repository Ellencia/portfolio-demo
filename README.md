# portfolio-demo

업무 자동화 포트폴리오용 폰 화면 데모 (9:16). 화면의 데이터는 모두 예시입니다.

**바로 보기: https://ellencia.github.io/portfolio-demo/**

- `excel.html` — 엑셀 자동 정리: 양식이 제각각인 결과보고 통합, 검증, 대시보드, 영수증 증빙, 공유 엑셀 보호
- `harness.html` — 메신저 업무 봇 두 개와 기록 DB를 잇는 업무 자동화. 디자인 5종(기본·다크 앱·폰 목업·메모장·브랜드, `harness-themes.css`)
- `bapl.html` — 직접 만든 구매관리 웹앱의 실제 화면(폰 폭 캡처, `img/`). 데이터는 `bapl/seed_demo.py` 가 만든 가상 회사 DB, `bapl/capture.py` 가 이야기 단계마다 DB 를 바꿔 가며 전·후 화면을 찍음
- `cad.html` — 사내 도면 1만 3천 개를 안의 글자로 찾는 검색기의 작동 방식. 도면은 SVG 로 그린 예시, 성능 수치만 실제 운영값
- `forms.html` — 장비 교정 만료 관리 + 한글(HWPX) 제출 양식 자동 작성. 데이터·회사명은 가상
- `imp.html` — 해외 수입 서류 사전 점검 웹앱. 실제 앱이 폰 폭에 맞지 않아 같은 색으로 다시 그렸고 수입 건은 가상
- `dl.html` — 다운로드 파일 자동 이름·폴더 정리 크롬 확장. 파일·업체명은 가상
- `tabrip.html` — 유튜브 기타 탭 영상을 Guitar Pro 악보로 바꾸는 tab-ripper(개인 프로젝트). 첫 장면의 링크 붙여넣기 앱은 구상안, 숫자는 실제 산출
- `b2b.html` — PC 교체 현장의 IP·프린터·백업을 기록하는 my-b2b-apps(AI 에이전트와 만든 첫 앱)의 실제 화면. `b2b/seed.js` 가 가상 고객사를 localStorage 에 넣고 `b2b/capture.py` 가 폰 폭으로 찍음(폰 폭에서 꺾이는 곳만 캡처용 CSS 로 덮음, 앱 코드는 그대로)
- `demo.css` · `demo.js` — 공용 스타일과 재생 (장면 길이 = 애니메이션이 끝나는 시각 + 3.5초)
- `sfx.py` — 영상 효과음(numpy 합성, 음원 파일 없음). 소리 시각은 `demo.js` 의 클래스별 기본표, 요소의 `data-sfx="소리"`·`data-sfx-at="초:소리 ..."`
- `bgm/` — 직접 쓴 배경음 후보(MIDI). `bgm/compose.py` 가 멜로디·코드로 `uke_whistle`(우쿨렐레+휘파람)·`marimba_shuffle`(마림바 셔플)·`musicbox_waltz`(오르골 왈츠) 전곡(약 95–107초)을 만듦. 저작권 걱정 없음

## 만들기

```
python render_cards.py                      # out/cards/ 에 장면별 1080x1920 PNG (설치된 크롬 헤드리스)
.venv\Scripts\python make_video.py harness  # out/video/harness.mp4 (pip install playwright av)
.venv\Scripts\python make_video.py tabrip --sfx  # 효과음 트랙까지 (pip install numpy)
.venv\Scripts\python make_video.py tabrip --sfx --bgm music/pixabay-600484-kids-ukulele.mp3  # 배경음 (waltz·arp 는 합성 기타)
.venv\Scripts\python make_video.py b2b --sfx --bgm bgm/musicbox_waltz.mid  # 직접 쓴 곡 (FluidSynth + GM 사운드폰트)
python bgm/compose.py                       # bgm/*.mid 다시 만들기 (+ 들어 보기용 wav, 커밋 안 함)
```

`.mid` 렌더에는 FluidSynth 와 GM 사운드폰트가 필요합니다. 경로는 환경변수 `FLUIDSYNTH_EXE`·`BGM_SF2` 로 바꿉니다(기본값은 작업 PC 경로, 사운드폰트는 FluidR3 GM).

배경음 원본은 `music/` 에 받아 두고 커밋하지 않습니다(Pixabay 라이선스: 음원 단독 배포 금지).
`out/video/tabrip.mp4` 배경음: [Kids Ukulele Music — 331music](https://pixabay.com/music/happy-childrens-tunes-kids-ukulele-music-600484/) (Pixabay Content License, 2026-10-25 기준 Content ID 미등록).

`python build_site.py` 는 GitHub Pages 용 `docs/` 를 만듭니다. `make_video.py` 는 화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 H.264 로 묶습니다.

## 상태 (2026-10-26)

- **글쓰기 기준**: 화면 글은 처음 보는 사람이 화면만 보고 이해해야 합니다. 장면마다 무슨 문제인지 먼저 말하고, 업계 약어·검사 용어(PASS 등)·설명 없는 점수는 빼거나 일상어로 바꿉니다. 숫자는 장면당 와닿는 것 하나만 씁니다.
- **다시 쓸 편**(압축이 심한 순): `imp` → `harness` → `bapl` → `forms` → `cad` → `excel`. `tabrip`·`b2b`·`dl` 은 양호합니다.
- **검사 방안**(아직 안 함): 맥락 없는 에이전트에게 `out/cards/*.png` 만 보여 주고 장면마다 뜻을 설명하게 해서, 못 알아듣는 장면을 찾습니다.
- **다음 새 편**: 3D 조립 검사기(cad-lab, 미스미 inCAD 공개 예제만). three.js 장면 + 가짜 커서로 돌려 보는 연출, 주인공은 검사기입니다. AI가 빼는 길을 제안하고 검사기가 "여기서 걸립니다"라고 거부하는 과정(창문 빼기), 문을 젖히다 볼트 머리에 걸리는 장면을 씁니다. 첫 작업은 헤드리스 크롬에서 WebGL 화면이 찍히는지 확인하는 것입니다.
- **금지**: 회사 도면·실제 고객·매물 데이터. 예시 데이터로 바꿉니다.

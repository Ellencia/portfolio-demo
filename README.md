# portfolio-demo

업무 자동화 포트폴리오용 폰 화면 데모 (9:16). 화면의 데이터는 모두 예시입니다.

**바로 보기: https://ellencia.github.io/portfolio-demo/**

- `excel.html` — 엑셀 자동 정리: 양식이 제각각인 결과보고 통합, 검증, 대시보드, 영수증 증빙, 공유 엑셀 보호
- `harness.html` — 메신저 업무 봇 두 개와 기록 DB를 잇는 업무 자동화. 디자인 5종(기본·다크 앱·폰 목업·메모장·브랜드, `harness-themes.css`)
- `bapl.html` — 직접 만든 구매관리 웹앱의 실제 화면(폰 폭 캡처, `img/`). 데이터는 `bapl/seed_demo.py` 가 만든 가상 회사 DB, `bapl/capture.py` 가 이야기 단계마다 DB 를 바꿔 가며 전·후 화면을 찍음
- `cad.html` — 사내 도면 1만 3천 개를 안의 글자로 찾는 검색기의 작동 방식. 도면은 SVG 로 그린 예시, 성능 수치만 실제 운영값
- `forms.html` — 장비 교정 만료 관리 + 한글(HWPX) 제출 양식 자동 작성. 데이터·회사명은 가상
- `imp.html` — 첫 해외 수입을 맡은 구매 담당이 용어·절차를 몰라 만든 사전점검 웹앱(점검표 + 용어집). 실제 앱이 폰 폭에 맞지 않아 같은 색으로 다시 그렸고 수입 건은 가상
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

## 상태 (2026-10-27)

### 어디까지 됐나

이 저장소는 회차 대신 편 단위로 진행합니다. 회귀 시험은 해당 없음(데모 저장소).

| 편 | html 마지막 변경 | 영상 | 글 점검 |
| --- | --- | --- | --- |
| imp | 6dd5dc3 | 최신 (6dd5dc3) | 다시 씀 (서사 교체, 처음 보는 사람 시험 9문항 통과 — Haiku 1번 0/3 은 위치 편향이라 통과로 침, 사용자 판정 10-27) |
| harness | 0d9e632 | 최신 (0d9e632, `--sfx --bgm bgm/lofi_keys.mid` — 커밋 메시지엔 없고 사용자 확인 10-27) | 다시 씀 (손으로 옮겨 적던 다섯 경로 → 봇 둘, 시험 8문항 중 2–8 Opus·Haiku 3/3, 1번 Haiku 1/3 → 순서 재확인 6/6, 화면 탓 아님) |
| bapl | d1f42f4 | 최신 (d1f42f4, `--sfx --bgm bgm/bossa_flute.mid`) | 다시 씀 (발주 한 건 따라가기, 시험 8문항 Opus 3/3 전부, Haiku 2·5·8번 2/3·나머지 3/3, 7번은 두 카드 중 하나만 맞아도 통과로 사용자 결정) |
| forms | 043a8c7 | 최신 (043a8c7, `--sfx --bgm bgm/baroque_oboe.mid`) | 다시 씀 (장비 목록을 서류에 매번 다시 적는 일 → 직접 만든 프로그램, 시험 8문항 Opus 3/3 전부, Haiku 1번 2/3 → 순서 재확인 6/6 화면 탓 아님·나머지 3/3. 1차 표지는 1번 0/3·2번 1/3, `out/quiz/forms/report_v1.md`) |
| cad | 84725a4 | 최신 (6d34b5d) | 다시 쓸 편 5 |
| excel | e380f0e | 최신 (6d34b5d, 배경음) | 다시 쓸 편 6 |
| tabrip | e380f0e | 최신 (e380f0e) | 양호 |
| b2b | ccdcbce | 최신 (ccdcbce) | 양호 |
| dl | 9b44572 | 최신 (40ef42b) | 양호 |

- "영상 최신" = 영상의 마지막 렌더 커밋이 html 마지막 변경과 같거나 나중(`git log --follow`, out/ 폴더 이동 커밋 077c50b 는 건너뜀). 작업 트리 깨끗함. `main` 이 `origin/main`(d1f42f4)보다 1커밋 앞섬: forms 커밋 043a8c7 아직 푸시 안 함.
- `docs/` 는 소스와 같습니다(스크래치 복사본에서 `build_site.py` 를 돌린 결과와 `diff -rq` 차이 없음: 페이지 9·index·영상 9·img 46). 장면 카드 수 = 각 html 장면 수(9편 전부, harness 는 디자인 5종 × 7장).
- 사이트 첫 화면 카드 설명은 `build_site.py` 의 PAGES 에 있습니다. 편을 다시 쓰면 이 문구도 같이 봅니다(imp·harness·bapl·forms 는 새 서사로 바꿈).
- harness 의 실제 구조 출처는 회사 PC 압축본 `STC_Outbox/2026-10-26/harness_src_2026-10-26.zip` 안 `shared-tools/하네스.md`(부품 지도)·`work-inbox/README.md`(받는 봇). 데모는 일반 이름(받는 봇·실행 봇·기록 DB·ERP)만 씁니다.

### 다음

1. 화면 글 다시 쓰기, 위 표의 "다시 쓸 편" 순서대로(남은 것: cad → excel). 한 편 고치면 그 칸을 "다시 씀(커밋)"으로 바꿉니다. 기준: 처음 보는 사람이 화면만 보고 이해, 장면마다 무슨 문제인지 먼저, 업계 약어·검사 용어(PASS 등)·설명 없는 점수는 빼거나 일상어로, 숫자는 장면당 하나.
2. 검사: 카드 PNG 만 모델(Opus·Haiku)에게 보여 주고 정답 기준이 있는 문제를 풀게 해 틀린 문항을 찾기(자기 보고 "모르는 단어"는 늘 뭔가를 채워 넣어 쓸모없었음). `quiz.py submit|wait|grade <편>`(문항·정답 기준은 파일 안 `QUESTIONS`, 기준은 사용자가 확인한 것만), 결과는 `out/quiz/<편>/report.md`. 객관식 1번 오답은 `quiz.py order <편>` 으로 재확인(보기 1·2 바꾼 판 + 원순서에 이유 요구, Haiku 3회씩) — harness·forms 는 6/6 화면 탓 아님, imp 는 순서를 바꿔도 늘 2번이라 위치 편향(`out/quiz/imp/q1_order.jsonl`). 편을 다시 쓸 때마다 그 편 문항을 `QUESTIONS` 에 추가하고 돌림(cad·excel 은 아직 문항 없음).
3. 새 편 3D 조립 검사기(cad-lab, 미스미 inCAD 공개 예제만, three.js + 가짜 커서, 주인공은 AI 제안을 "여기서 걸립니다"로 거부하는 검사기 — 창문 빼기, 문 젖히다 볼트 머리에 걸림). 첫 작업은 헤드리스 크롬에서 WebGL 화면이 찍히는지 확인.

### 하면 안 되는 것

- 회사 도면·실제 고객·매물 데이터. 예시 데이터로 바꿉니다.
- `quiz.py order` 는 그 편 `QUESTIONS` 첫 문항이 "… 보기 중 하나의 번호만: 1) … 2) …" 꼴, 보기 4개, 정답 1 일 때만 돕니다(`assert`). 새 편 1번 문항도 이 꼴로 씁니다.
- `docs/` 손 수정: `build_site.py` 가 통째로 지우고 다시 만듭니다. `b2b` 는 앱 코드를 고치지 않고 폰 폭에서 꺾이는 곳만 캡처용 CSS 로 덮습니다.
- `tabrip` 배경음은 일부러 고른 원래 곡이라 바꾸지 않습니다. `music/` 원본(Pixabay 단독 배포 금지)·`bgm/*.wav`·`STATUS.md`·`update.md` 는 커밋하지 않습니다.

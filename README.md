# portfolio-demo

업무 자동화 포트폴리오용 폰 화면 데모 (9:16). 화면의 데이터는 모두 예시입니다.

**바로 보기: https://ellencia.github.io/portfolio-demo/**

대표 업무 자동화 데모: **[하루의 업무가 일일보고로](https://ellencia.github.io/portfolio-demo/harness_a.html)** · [MP4](https://ellencia.github.io/portfolio-demo/video/harness_a.mp4)

## 다른 데모를 만드는 사람을 위한 가이드

이 저장소의 데모를 만들며 반복해서 고친 문제를 **[이해되는 데모 만들기](skills/demo-storytelling/SKILL.md)**로 정리했습니다. 제품·업무 도구의 웹 데모와 영상에 적용할 수 있는 한국어 가이드이자 AI용 스킬입니다.

핵심은 **설명 문장을 줄인 자리를, 알아볼 수 있는 과정으로 채우는 것**입니다. 사실과 증거 → 처음 보는 사람의 이해 → 관람 경로 → 읽는 시간과 움직임 → 최종 산출물 검수 순서로 판단합니다. 글을 줄이면서 맥락까지 없애거나, 설명용 연출을 실제 구현처럼 보이게 만드는 문제를 다룹니다.

- [SKILL.md](skills/demo-storytelling/SKILL.md): 공통 기준과 작업 순서
- [장면 설계 예시](skills/demo-storytelling/references/scene-design.md): 견적서 입력, 사진 판독, 통화에서 할 일로 이어지는 장면
- [최종 산출물 검수](skills/demo-storytelling/references/artifact-review.md): 이해·화면·재생·음향·배포본 확인

사람은 위 문서를 바로 읽고 사용할 수 있습니다. AI에는 `skills/demo-storytelling/SKILL.md`를 읽고 적용하도록 요청하세요. 스킬을 지원하는 환경에서는 `skills/demo-storytelling/` 폴더 전체를 등록해 사용합니다. 환경에 따라 등록 방법은 다릅니다.

요청 예시:

> 이 저장소의 `skills/demo-storytelling/SKILL.md`를 읽고 이 데모를 점검해 줘. 먼저 실제 재생본을 확인하고, 처음 보는 사람이 이해하기 어려운 장면과 근거를 짚어 줘. 이번에는 수정하지 마.

> 이 저장소의 `skills/demo-storytelling/SKILL.md`를 적용해 견적서 입력 데모를 만들어 줘. 실제 앱 화면과 예시 데이터를 사용하고, 대표 장면 하나를 먼저 검수한 뒤 나머지 장면으로 확장해 줘.

이 가이드는 특정 디자인이나 엔진을 요구하지 않습니다. 실제 사용자 피드백을 일반화한 작업 기준이며, 기존 데모 전부가 이 기준으로 검수되었다는 뜻은 아닙니다.

## 데모 구성

- `harness_a.html` — 대표 데모. 견적 메일 → 발주 → 통화 → 일일보고를 따라가며 퇴근으로 끝나는 본편 5장면. 구성 설명과 날짜가 있는 자동 점검 기록은 데모 아래 펼쳐보는 부록에 둠. 설명용 재현 화면·예시 데이터이며, 자동 점검 결과는 지정 항목의 통과만 뜻함.
- `harness_b.html` · `harness_c.html` — 전후 비교 / 확인과 결재 구성. 홈페이지에서 다른 구성으로 연결.
- `excel.html` — 엑셀 자동 정리: 양식이 제각각인 결과보고 통합, 검증, 대시보드, 영수증 증빙, 공유 엑셀 보호
- `harness.html` — 메신저 업무 봇 두 개와 기록 DB를 잇는 업무 자동화. 디자인 5종(기본·다크 앱·폰 목업·메모장·브랜드, `harness-themes.css`)
- `bapl.html` — 직접 만든 구매관리 웹앱의 실제 화면(폰 폭 캡처, `img/`). 데이터는 `bapl/seed_demo.py` 가 만든 가상 회사 DB, `bapl/capture.py` 가 이야기 단계마다 DB 를 바꿔 가며 전·후 화면을 찍음
- `cad.html` — 사내 도면 1만 3천 개를 안의 글자로 찾는 검색기의 작동 방식. 도면은 SVG 로 그린 예시, 성능 수치만 실제 운영값
- `forms.html` — 장비 교정 만료 관리 + 한글(HWPX) 제출 양식 자동 작성. 데이터·회사명은 가상
- `imp.html` — 첫 해외 수입을 맡은 구매 담당이 용어·절차를 몰라 만든 사전점검 웹앱(점검표 + 용어집). 실제 앱이 폰 폭에 맞지 않아 같은 색으로 다시 그렸고 수입 건은 가상
- `dl.html` — 다운로드 파일 자동 이름·폴더 정리 크롬 확장. 파일·업체명은 가상
- `tabrip.html` — 유튜브 기타 탭 영상을 Guitar Pro 악보로 바꾸는 tab-ripper(개인 프로젝트). 첫 장면의 링크 붙여넣기 앱은 구상안, 숫자는 실제 산출
- `b2b.html` — PC 교체 현장의 IP·프린터·백업을 기록하는 my-b2b-apps(AI 에이전트와 만든 첫 앱)의 실제 화면. `b2b/seed.js` 가 가상 고객사를 localStorage 에 넣고 `b2b/capture.py` 가 폰 폭으로 찍음(폰 폭에서 꺾이는 곳만 캡처용 CSS 로 덮음, 앱 코드는 그대로)
- `ocr.html` — score-ocr(개인 프로젝트, 저장소 비공개)의 4장면 데모. 실제 판독 MusicXML의 음표 편집 → 빠진 마지막 음 비교 → 여러 판독의 선택 기준 → 별도 왈츠 검증 기록. 하바네라 1883년 판 스캔과 촬영 효과를 공개 시연에 사용하며, 보정 장면은 설명용임을 표시. 부록에서 음높이 전후 비교와 MusicXML 다운로드 가능. 자료·선택 규칙·측정 범위는 [ocr/DEMO_NOTES.md](ocr/DEMO_NOTES.md).
- `demo.css` · `demo.js` — 공용 스타일과 재생 (장면 길이 = 애니메이션이 끝나는 시각 + 3.5초)
- `sfx.py` — 영상 효과음(numpy 합성, 음원 파일 없음). 소리 시각은 `demo.js` 의 클래스별 기본표, 요소의 `data-sfx="소리"`·`data-sfx-at="초:소리 ..."`
- `bgm/` — 직접 쓴 배경음 후보(MIDI). `bgm/compose.py` 가 멜로디·코드로 `uke_whistle`(우쿨렐레+휘파람)·`marimba_shuffle`(마림바 셔플)·`musicbox_waltz`(오르골 왈츠) 전곡(약 95–107초)을 만듦. 저작권 걱정 없음

## 만들기

```
pip install playwright av numpy Pillow     # 설치된 Chrome 사용
python render_cards.py                      # out/cards/ 에 장면별 1080x1920 PNG (설치된 크롬 헤드리스)
.venv\Scripts\python make_video.py harness  # out/video/harness.mp4 (pip install playwright av)
.venv\Scripts\python make_video.py tabrip --sfx  # 효과음 트랙까지 (pip install numpy)
.venv\Scripts\python make_video.py tabrip --sfx --bgm music/pixabay-600484-kids-ukulele.mp3  # 배경음 (waltz·arp 는 합성 기타)
.venv\Scripts\python make_video.py b2b --sfx --bgm bgm/musicbox_waltz.mid  # 직접 쓴 곡 (FluidSynth + GM 사운드폰트)
python bgm/compose.py                       # bgm/*.mid 다시 만들기 (+ 들어 보기용 wav, 커밋 안 함)
```

하네스 A·B·C를 수정한 뒤에는 카드 → 영상 → 사이트 순서로 갱신합니다. 카드와 영상은 웹 글꼴과 효과 초기화가 끝난 뒤 캡처하며, 페이지 스크립트 오류가 있으면 실패합니다.

```
python render_cards.py harness_a harness_b harness_c
python make_video.py harness_a --sfx --bgm bgm/pop_xylo.mid
python make_video.py harness_b --sfx
python make_video.py harness_c --sfx
python fx_check.py harness_a.html
python build_site.py
```

A MP4는 효과음 + 배경음 `bgm/pop_xylo.mid`(A장조 광고 팝, 전주·A·B 16마디가 41.5초 동안 한 번만 지나감, 장면 HOLD 1.7초), B·C MP4는 효과음만 있고 배경음 없음입니다. 기존 본편의 영상·음악은 유지합니다. 홈페이지 대표작은 A·구매관리·현장 IP 관리이며, 나머지 데모와 기존 본편도 계속 열 수 있습니다. 썸네일은 저장된 카드에서 생성합니다.

`fx_check.py`는 글자·불투명도·위치와 SVG 선의 그려지는 진행·경로를 비교합니다. 실제 카드·최종 MP4 프레임·공개 페이지 확인과 음향 청취는 별도 검수입니다. `docs/`는 직접 수정하지 않고 `build_site.py`로 만듭니다.

2026-11-09 생성본 확인: A 59.1초·B 28.4초·C 26.6초, 모두 1080×1920/30fps. 카드 15장과 웹·인코딩된 영상의 각 장면 끝을 대조했고, A의 6장면 시계 검사와 검사기 정상/의도적 실패 예제를 확인했습니다. 영상 진행 막대는 카드에서 숨기는 기존 규칙을 유지합니다. 홈페이지는 데스크톱·모바일 폭, 로컬 파일 연결 121개를 확인했습니다. 효과음은 트랙과 피크 검사까지 확인했으며 청취 평가는 별도입니다.

2026-11-10 A 갱신: 본편은 5장면·50.5초이며, 구성 설명과 2026-10-25 자동 점검 기록은 접힌 부록으로 옮겼습니다. 카드 5장과 MP4를 다시 생성하고 이전 6번째 카드는 삭제했습니다. 5장면 모두 재생·영상 시계 검사와 카드·최종 MP4 끝 프레임 대조를 통과했습니다. 부록은 1440·390·320px 폭 및 모바일 다크 모드에서 확인했으며, 키보드 열기/닫기, 펼칠 때 폰 크기 유지, 5→1 반복, 녹화 화면에서 부록 숨김을 검사했습니다. 효과음은 트랙·피크 검사까지 확인했고 청취 평가는 별도입니다.

2026-11-10 OMR 재구성: 본편 4장면과 음표 비교·자료 설명 부록. 36→5는 왈츠 219마디의 음높이·길이·붙임줄 비교 기록이며, 하바네라 시연 및 연주 표시 보정과 구분했습니다. 실제 MusicXML에서 첫 음 F4→G4만 변경됨을 검사하고, 웹의 음높이 재생·파일 선택·모바일 부록·장면 범위와 재생 시계를 확인했습니다. 새 카드와 MP4는 같은 소스에서 생성합니다. 기존 4중주 편곡은 유지하되 FluidR3 계열 SoundFont를 다시 렌더링했고, 음높이 비교 구간은 반주를 낮춥니다. 자세한 재생성 절차와 음향 검증 한계는 `ocr/DEMO_NOTES.md`에 있습니다.

`.mid` 렌더에는 FluidSynth 와 GM 사운드폰트가 필요합니다. 경로는 환경변수 `FLUIDSYNTH_EXE`·`BGM_SF2` 로 바꿉니다(기본값은 작업 PC 경로, 사운드폰트는 FluidR3 GM).

배경음 원본은 `music/` 에 받아 두고 커밋하지 않습니다(Pixabay 라이선스: 음원 단독 배포 금지).
`out/video/tabrip.mp4` 배경음: [Kids Ukulele Music — 331music](https://pixabay.com/music/happy-childrens-tunes-kids-ukulele-music-600484/) (Pixabay Content License, 2026-10-25 기준 Content ID 미등록).
`out/video/ocr.mp4` 배경음: 비제 「하바네라」 1–19마디를 Choudens 보컬 스코어([1883](https://archive.org/details/carmenopracomi00bize)·[1900](https://archive.org/details/carmenopraen4act00bize))에서 읽어 `ocr/make_bgm.py` 로 첼로 4대에 직접 편곡(노래 = 활, 피아노 파트 = 피치카토, ♩=72 → 58)하고 FluidSynth 로 합성. 결과 `music/habanera_quartet.mid` 는 커밋 안 함.

`python build_site.py` 는 GitHub Pages 용 `docs/` 를 만듭니다. `make_video.py` 는 화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 H.264 로 묶습니다.

## 이전 작업 기록 (2026-11-08)

아래 표와 다음 작업 목록은 당시 기록입니다. 하네스 A·B·C의 공개 연결과 생성 절차는 위의 최신 안내를 따릅니다.

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
| ocr | 2026-11-10 재구성 | 같은 소스에서 재생성 (`--sfx --sfx-db -10 --bgm music/habanera_quartet.wav`) | 실제 파일 편집·원본 대조·선택 원리·별도 검증 기록, 별도 관람자 이해 평가는 미실시 |

- "영상 최신" = 영상의 마지막 렌더 커밋이 html 마지막 변경과 같거나 나중(`git log --follow`, out/ 폴더 이동 커밋 077c50b 는 건너뜀). 작업 트리 깨끗함. `main` 과 `origin/main` 같음(98d5f03).
- `docs/` 는 소스와 같습니다(스크래치 복사본에서 `build_site.py` 를 돌린 결과와 `diff -rq` 차이 없음: 페이지 9·index·영상 9·img 46). 장면 카드 수 = 각 html 장면 수(9편 전부, harness 는 디자인 5종 × 7장).
- 사이트 첫 화면 카드 설명은 `build_site.py` 의 PAGES 에 있습니다. 편을 다시 쓰면 이 문구도 같이 봅니다(imp·harness·bapl·forms 는 새 서사로 바꿈).
- harness 의 실제 구조 출처는 회사 PC에서 가져온 2026-10-26 압축본(git 밖) 안 `shared-tools/하네스.md`(부품 지도)·`work-inbox/README.md`(받는 봇). 데모는 일반 이름(받는 봇·실행 봇·기록 DB·ERP)만 씁니다.

### 다음

0. harness 광고형 시안 고르기(11-08 사용자: "일을 쉽게 처리하고 있다는 걸 광고하는 느낌"). `harness_a.html`(하루 압축, 결과 먼저·큰 시계)·`harness_c.html`(누른 횟수 0→3) 초안 6장면씩, 카드만 찍음·영상 없음. B(전후 대비)는 예전 손작업 시간 세 개(견적서 입력·메일 첨부 정리·일일보고)를 사용자에게 받아야 만듦. 이 편만 "문제 먼저" 원칙 예외. 고른 판이 `harness.html` 을 대체하면 `build_site.py` PAGES 문구도 바꿈. C의 "누른 횟수"는 사진 보내기를 안 셈(문구 결정 대기). 아티팩트 도구가 있는 세션에서 이어 갈 것.
1. 화면 글 다시 쓰기, 위 표의 "다시 쓸 편" 순서대로(남은 것: cad → excel). 한 편 고치면 그 칸을 "다시 씀(커밋)"으로 바꿉니다. 기준: 처음 보는 사람이 화면만 보고 이해, 장면마다 무슨 문제인지 먼저, 업계 약어·검사 용어(PASS 등)·설명 없는 점수는 빼거나 일상어로, 숫자는 장면당 하나.
2. 검사: 카드 PNG 만 모델(Opus·Haiku)에게 보여 주고 정답 기준이 있는 문제를 풀게 해 틀린 문항을 찾기(자기 보고 "모르는 단어"는 늘 뭔가를 채워 넣어 쓸모없었음). `quiz.py submit|wait|grade <편>`(문항·정답 기준은 파일 안 `QUESTIONS`, 기준은 사용자가 확인한 것만), 결과는 `out/quiz/<편>/report.md`. 객관식 1번 오답은 `quiz.py order <편>` 으로 재확인(보기 1·2 바꾼 판 + 원순서에 이유 요구, Haiku 3회씩) — harness·forms 는 6/6 화면 탓 아님, imp 는 순서를 바꿔도 늘 2번이라 위치 편향(`out/quiz/imp/q1_order.jsonl`). 편을 다시 쓸 때마다 그 편 문항을 `QUESTIONS` 에 추가하고 돌림(cad·excel 은 아직 문항 없음).
3. 새 편 3D 조립 검사기(cad-lab, 미스미 inCAD 공개 예제만, three.js + 가짜 커서, 주인공은 AI 제안을 "여기서 걸립니다"로 거부하는 검사기 — 창문 빼기, 문 젖히다 볼트 머리에 걸림). 첫 작업은 헤드리스 크롬에서 WebGL 화면이 찍히는지 확인.

### 하면 안 되는 것

- 회사 도면·실제 고객·매물 데이터. 예시 데이터로 바꿉니다.
- `quiz.py order` 는 그 편 `QUESTIONS` 첫 문항이 "… 보기 중 하나의 번호만: 1) … 2) …" 꼴, 보기 4개, 정답 1 일 때만 돕니다(`assert`). 새 편 1번 문항도 이 꼴로 씁니다.
- `docs/` 손 수정: `build_site.py` 가 통째로 지우고 다시 만듭니다. `b2b` 는 앱 코드를 고치지 않고 폰 폭에서 꺾이는 곳만 캡처용 CSS 로 덮습니다.
- `tabrip` 배경음은 일부러 고른 원래 곡이라 바꾸지 않습니다. `music/` 원본(Pixabay 단독 배포 금지)·`bgm/*.wav`·`STATUS.md`·`update.md` 는 커밋하지 않습니다.

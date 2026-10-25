# portfolio-demo

업무 자동화 포트폴리오용 폰 화면 데모 (9:16). 화면의 데이터는 모두 예시입니다.

**바로 보기: https://ellencia.github.io/portfolio-demo/**

- `excel.html` — 엑셀 자동 정리: 양식이 제각각인 결과보고 통합, 검증, 대시보드, 영수증 증빙, 공유 엑셀 보호
- `harness.html` — 메신저 업무 봇 두 개와 기록 DB를 잇는 업무 자동화. 디자인 5종(기본·다크 앱·폰 목업·메모장·브랜드, `harness-themes.css`)
- `bapl.html` — 직접 만든 구매관리 웹앱의 실제 화면(폰 폭 캡처, `img/`). 데이터는 `bapl/seed_demo.py` 가 만든 가상 회사 DB, `bapl/capture.py` 가 이야기 단계마다 DB 를 바꿔 가며 전·후 화면을 찍음
- `cad.html` — 사내 도면 1만 3천 개를 안의 글자로 찾는 검색기의 작동 방식. 도면은 SVG 로 그린 예시, 성능 수치만 실제 운영값
- `tabrip.html` — 유튜브 기타 탭 영상을 Guitar Pro 악보로 바꾸는 tab-ripper(개인 프로젝트). 첫 장면의 링크 붙여넣기 앱은 구상안, 숫자는 실제 산출
- `demo.css` · `demo.js` — 공용 스타일과 재생 (장면 길이 = 애니메이션이 끝나는 시각 + 3.5초)
- `sfx.py` — 영상 효과음(numpy 합성, 음원 파일 없음). 소리 시각은 `demo.js` 의 클래스별 기본표, 요소의 `data-sfx="소리"`·`data-sfx-at="초:소리 ..."`

## 만들기

```
python render_cards.py                      # out/ 에 장면별 1080x1920 PNG (설치된 크롬 헤드리스)
.venv\Scripts\python make_video.py harness  # out/harness.mp4 (pip install playwright av)
.venv\Scripts\python make_video.py tabrip --sfx  # 효과음 트랙까지 (pip install numpy)
.venv\Scripts\python make_video.py tabrip --sfx --bgm music/pixabay-600484-kids-ukulele.mp3  # 배경음 (waltz·arp 는 합성 기타)
```

배경음 원본은 `music/` 에 받아 두고 커밋하지 않습니다(Pixabay 라이선스: 음원 단독 배포 금지).
`out/tabrip.mp4` 배경음: [Kids Ukulele Music — 331music](https://pixabay.com/music/happy-childrens-tunes-kids-ukulele-music-600484/) (Pixabay Content License, 2026-10-25 기준 Content ID 미등록).

`python build_site.py` 는 GitHub Pages 용 `docs/` 를 만듭니다. `make_video.py` 는 화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 H.264 로 묶습니다.

# portfolio-demo

업무 자동화 포트폴리오용 폰 화면 데모 (9:16). 화면의 데이터는 모두 예시입니다.

- `excel.html` — 엑셀 자동 정리: 양식이 제각각인 결과보고 통합, 검증, 대시보드, 영수증 증빙, 공유 엑셀 보호
- `harness.html` — 메신저 업무 봇 두 개와 기록 DB를 잇는 업무 자동화. 디자인 5종(기본·다크 앱·폰 목업·메모장·브랜드, `harness-themes.css`)
- `demo.css` · `demo.js` — 공용 스타일과 재생 (장면 길이 = 애니메이션이 끝나는 시각 + 3.5초)

## 만들기

```
python render_cards.py                      # out/ 에 장면별 1080x1920 PNG (설치된 크롬 헤드리스)
.venv\Scripts\python make_video.py harness  # out/harness.mp4 (pip install playwright av)
```

`make_video.py` 는 화면녹화가 아니라 프레임마다 애니메이션 시각을 맞춰 찍어 H.264 로 묶습니다.

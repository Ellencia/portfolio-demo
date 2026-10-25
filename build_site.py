"""GitHub Pages 용 docs/ 를 만든다 — 아티팩트용 html 에 문서 머리(doctype·charset·viewport)를 붙이고 css·js·이미지·영상을 복사.

실행: python build_site.py  ->  docs/ (index.html + excel·harness·bapl.html)
공개 주소: https://ellencia.github.io/portfolio-demo/
"""
import shutil
from pathlib import Path

HERE = Path(__file__).parent
DOCS = HERE / "docs"
PAGES = [("bapl", "구매관리 웹앱", "발주부터 세금계산서까지, 직접 만든 웹앱의 실제 화면 (데이터는 가상)"),
         ("harness", "업무 자동화", "메신저 업무 봇 두 개와 기록 DB를 잇는 흐름. 디자인 5종"),
         ("cad", "도면 검색기", "도면 1만 3천 개를 안의 글자로 찾고, AI 가 근거를 달아 답함 (도면은 예시 그림)"),
         ("forms", "장비 대장 · 제출 서류", "교정 만료를 날짜 순으로 챙기고, 한글(HWPX) 양식을 대장 값으로 채움"),
         ("imp", "수입 서류 점검", "PI·패킹리스트·B/L 을 서로 대조해 송금·선적 전에 안 맞는 곳을 찾고 수입 원가까지"),
         ("dl", "다운로드 자동 정리", "받는 순간 파일 이름을 규칙대로 바꾸고 폴더로 나누는 크롬 확장"),
         ("excel", "엑셀 자동 정리", "양식이 제각각인 엑셀을 한 표로, 검증과 대시보드까지"),
         ("tabrip", "탭 영상 → 악보", "유튜브 기타 탭 영상을 연주할 Guitar Pro 악보로 (개인 프로젝트, 숫자는 실제 산출)"),
         ("b2b", "현장 IP 관리 앱", "PC 설치·교체·유지보수용 CRM, 코딩 공부 없이 Gemini CLI로 만든 첫 앱의 실제 화면 (데이터는 가상)")]
HEAD = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n' \
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'

if DOCS.exists():
    shutil.rmtree(DOCS)
(DOCS / "video").mkdir(parents=True)
for f in ("demo.css", "demo.js", "harness-themes.css"):
    shutil.copy(HERE / f, DOCS / f)
shutil.copytree(HERE / "img", DOCS / "img", ignore=shutil.ignore_patterns("*.json"))
for page, *_ in PAGES:
    src = (HERE / f"{page}.html").read_text(encoding="utf-8")
    body = src.index('<div class="phone"')  # 그 앞(제목·글꼴·스타일)은 머리로
    (DOCS / f"{page}.html").write_text(HEAD + src[:body] + "</head>\n<body>\n" + src[body:] + "\n</body>\n</html>\n",
                                       encoding="utf-8")
    shutil.copy(HERE / "out" / "video" / f"{page}.mp4", DOCS / "video" / f"{page}.mp4")

cards = "\n".join(f'''    <li><b>{name}</b><span>{desc}</span>
      <p><a href="{page}.html">데모 보기</a><a href="video/{page}.mp4">영상 (MP4)</a></p></li>''' for page, name, desc in PAGES)
(DOCS / "index.html").write_text(HEAD + f'''<title>업무 자동화 포트폴리오</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=IBM+Plex+Sans+KR:wght@400;700&display=swap">
<style>
:root {{ --bg: #F4F5F0; --fg: #17212B; --sub: #5B6670; --line: #D3D8CE; --card: #FFFFFF; --marker: #FFD84A }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #12171C; --fg: #E3E7E0; --sub: #98A2AA; --line: #2E3740; --card: #1C232A; color-scheme: dark }} }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.6 "IBM Plex Sans KR", "Malgun Gothic", sans-serif;
  padding: 48px max(16px, env(safe-area-inset-left)) 48px max(16px, env(safe-area-inset-right)) }}
main {{ max-width: 640px; margin: 0 auto }}
h1 {{ font: 400 34px/1.2 "Black Han Sans", sans-serif; margin: 0 0 8px }}
h1 mark {{ background: linear-gradient(transparent 58%, var(--marker) 58%); color: inherit }}
.lead {{ color: var(--sub); margin: 0 0 28px }}
ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px }}
li {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; display: grid; gap: 2px }}
li b {{ font-size: 17px }} li span {{ color: var(--sub); font-size: 14px }}
li p {{ margin: 8px 0 0; display: flex; gap: 8px; flex-wrap: wrap }}
li a {{ color: var(--fg); text-decoration: none; border: 1px solid var(--line); border-radius: 8px; padding: 5px 12px; font-size: 14px; font-weight: 700 }}
li a:first-child {{ background: var(--marker); border-color: var(--marker); color: #17212B }}
li a:focus-visible {{ outline: 2px solid var(--fg); outline-offset: 2px }}
footer {{ margin-top: 28px; color: var(--sub); font-size: 13px }}
</style>
</head>
<body>
<main>
  <h1>반복 업무를<br><mark>자동으로</mark></h1>
  <p class="lead">폰 화면 크기 데모 아홉 편. 업무 데모 화면의 회사·거래처·품목·금액은 모두 예시입니다.</p>
  <ul>
{cards}
  </ul>
  <footer>소스: <a href="https://github.com/Ellencia/portfolio-demo" style="color:inherit">github.com/Ellencia/portfolio-demo</a></footer>
</main>
</body>
</html>
''', encoding="utf-8")
print("docs:", sorted(p.name for p in DOCS.iterdir()))

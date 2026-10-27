"""처음 보는 사람 시험: 장면 카드 PNG 만 보고 문제를 풀게 한 뒤, 정답 기준으로 따로 채점한다.

실행: python quiz.py submit|wait|grade|order <페이지>   (카드는 render_cards.py 결과 out/cards/<페이지>_N.png)
결과: out/quiz/<페이지>/ 에 answers.jsonl(읽기 모델 원답)·judge.jsonl(채점 요청·응답 전체)·report.md
읽는 법: 시험 통과 ≠ 사람 이해, 틀린 문항을 찾는 도구. Haiku 객관식은 위치 편향(늘 2번)이 있으니 객관식 오답은
  `order` 로 재확인(보기 1·2 를 바꾼 판 + 원순서에 이유 요구, Haiku 직접 호출 N 회씩, q1_order.jsonl).
"""
import base64, json, os, re, sys, time
from pathlib import Path

HERE = Path(__file__).parent
CARDS = HERE / "out" / "cards"
MODELS = {"opus": "claude-opus-5-5", "haiku": "claude-haiku-5-5"}
N = 3

# 페이지별 (질문, 정답 기준). 1번은 객관식(정답 번호 한 글자), 나머지는 서술형(Opus 가 기준으로 채점).
# 기준은 사용자가 확인한 것만 적는다 — imp: 10-26 확인(구매 담당 첫 수입, 용어·절차 몰라서 만든 점검표+용어집)
QUESTIONS = {
    "imp": [
        ("이 영상이 소개하는 것은? 보기 중 하나의 번호만: 1) 직접 만든 프로그램  2) 수입할 때 알아 둘 요령·방법  3) 회사 광고  4) 모르겠음", "1"),
        ("이걸 만든 사람은 어떤 사람이고, 왜 만들었어?", "구매 담당(회사원)이 처음 해외 수입을 맡았는데 서류 이름·용어·절차를 몰라서"),
        ("모르는 약어가 나오면 이 프로그램에서 어떻게 해?", "용어집(용어 설명서)에서 검색하면 쉬운 뜻과 실무에서 확인할 것이 나온다"),
        ("배터리에는 무슨 문제가 있었어?", "주문(120개)보다 상자·서류에 적게(96개) 들어 있음, 빠진 만큼도 돈을 내게 되어 있음"),
        ("돈 보낼 계좌가 서류마다 다르면 왜 제일 먼저 확인해?", "가짜 계좌로 돈을 빼돌리는 사기일 수 있어서"),
        ("랜턴 원가에는 물건값 말고 무엇이 더 들어갔어? 둘 이상", "운송비·보험·관세·통관 수수료·창고·트럭 중 둘 이상"),
        ("이 수입 건은 지금 어느 단계이고, 무엇이 급해?", "통관 단계, 원산지 증명(관세 할인용)이 빠져 있음"),
        ("준비 점수가 31점에서 88점이 된 건 무슨 뜻이야? 왜 100점이 아니야?", "꼭 고칠 것·확인할 것이 줄어서 점수가 오름(감점식), 확인할 것이 남아서 100점이 아님"),
        ("이 프로그램이 대신 해 주지 않는 것은?", "통관 자체, 또는 세금 분류·안전 인증 판단(사람·관세사가 함)"),
    ],
    # harness: 10-26 확인(구매 담당, 손으로 옮겨 적던 일을 봇 둘이 받고 대신 입력)
    "harness": [
        ("이 영상이 소개하는 것은? 보기 중 하나의 번호만: 1) 직접 만든 프로그램  2) 업무 요령·방법  3) 회사 광고  4) 모르겠음", "1"),
        ("만든 사람은 어떤 일을 하고, 뭐가 불편했어?", "구매 담당. 말·메일·전화 등으로 들어온 일을 ERP·사업 폴더·일일보고에 손으로 옮겨 적어야 했음"),
        ("봇이 둘인데 각각 뭘 해?", "하나는 들어오는 일(말·메일·전화)을 할 일로 받아 두고, 하나는 시키면 ERP·기록에 대신 입력"),
        ("견적서 사진을 보내면 어떻게 돼?", "봇이 읽어서 발주서로 등록하고, 관련 할 일도 끝냄 처리"),
        ("메일 첨부 견적서는 어디로 가? 왜 봇이 판단해야 해?", "그 사업 폴더로. 업체 견적서엔 사업 이름이 잘 없어서 제목·품목으로 짚어야 함"),
        ("통화 녹음은 어떻게 쓰여?", "글로 바꿔 요약하고 할 일로 만듦. 회사 PC 안에서만 처리"),
        ("일일보고 초안에서 사람이 하는 일은?", "애매한 줄을 넣기/빼기로 고르면 됨(확실한 줄은 봇이 넣음)"),
        ("마지막 장면의 점검은 왜 있어?", "봇이 조용히 멈춰 있어도 모르니까 매일 아침 스스로 점검해 알려 줌"),
    ],
    # bapl: 10-26 다시 씀(주문한 물건이 어디쯤인지 회사 전산은 답이 없어서 만든 웹앱). 10-26 확인, 7번은 둘 중 하나면 통과(사용자 결정)
    "bapl": [
        ("이 영상이 소개하는 것은? 보기 중 하나의 번호만: 1) 직접 만든 프로그램  2) 업무 요령·방법  3) 회사 광고  4) 모르겠음", "1"),
        ("만든 사람은 왜 이 웹앱을 만들었어?", "주문한 물건이 지금 어디쯤 왔는지 회사 전산(ERP)으로는 알 수 없어서"),
        ("업체가 메신저로 '내일 배송'이라고 말하면 어떻게 돼?", "봇이 그 주문 건(발주서)의 진행 이력에 자동으로 기록"),
        ("물건이 도착해서 처리하면 화면에서 뭐가 바뀌어?", "늦은(납기 지남) 목록에서 빠지고 진행 단계 표시가 한 칸 나아감"),
        ("견적서 메일이 오면 할 일은 어디서 어디로 옮겨 가?", "'견적 기다리는 것'에서 '발주(주문) 넣을 것'으로"),
        ("첫 화면은 뭘 대신 세 줘?", "안 온 것·늦은 것·결재 기다리는 것 같은 건수를 모아 보여 줌"),
        ("이 앱은 회사 전산(ERP)과 어떤 관계야?", "회사 전산에 적던 것을 그대로 기록함, 또는 30분마다 전산 자료를 가져와 맞춤 (둘 중 하나만 있어도 정답)"),
        ("이 앱은 누가 만들었고 지금 어떻게 쓰여?", "혼자 만들어 매일 쓰는 중(실제 운영)"),
    ],
    # forms: 10-26 다시 씀(서류 낼 때마다 장비 목록을 한글에 다시 치던 일). 10-26 확인
    "forms": [
        ("이 영상이 소개하는 것은? 보기 중 하나의 번호만: 1) 직접 만든 프로그램  2) 업무 요령·방법  3) 회사 광고  4) 모르겠음", "1"),
        ("만든 사람은 뭐가 불편해서 이걸 만들었어?", "서류를 낼 때마다 장비 목록을 서류에 손으로 다시 적어야 하는 일이 많아서"),
        ("두 번째 장면의 목록에서 빨간 것은 무슨 뜻이야?", "측정기 검사(교정) 기한이 지난 것"),
        ("측정기 목록에 날짜를 넣으면 프로그램이 뭘 해 줘?", "남은 날을 세어 색을 바꾸고 기한 지난 것부터 보여 줌"),
        ("한글 서류는 어떻게 만들어져?", "한글 프로그램 없이 양식 파일의 표 칸을 장비 목록 값으로 채움(도장 자리까지)"),
        ("사진이 없는 설비는 서류에 어떻게 나와?", "칸을 비워 '사진 없음'으로 남겨 뭐가 빠졌는지 보이게 함"),
        ("제품 종류가 여러 개면 서류는 어떻게 만들어?", "제품을 골라 한 번에 만들고 한 묶음(zip) 파일로 받음"),
        ("만든 서류를 그냥 내지 않고 무엇을 더 했어?", "한글로 열어 인쇄 모양을 확인하고 틀어진 곳(서명란이 다음 쪽으로, 글자 벌어짐)을 고침"),
    ],
}

READ_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["answers"],
               "properties": {"answers": {"type": "array", "items": {
                   "type": "object", "additionalProperties": False, "required": ["q", "answer"],
                   "properties": {"q": {"type": "integer"}, "answer": {"type": "string"}}}}}}
JUDGE_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["grades"],
                "properties": {"grades": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False, "required": ["q", "correct", "why"],
                    "properties": {"q": {"type": "integer"}, "correct": {"type": "boolean"}, "why": {"type": "string"}}}}}}


def read_prompt(questions):
    return ("위 사진들은 인스타그램 릴스에서 넘겨 본 짧은 소개 영상의 장면들입니다(1번부터 순서대로).\n"
            "당신은 이 분야 일을 해 본 적 없는 일반인입니다. 화면에 보이는 것만으로 아래 질문에 짧게 답하세요.\n"
            "화면만으로 알 수 없으면 지어내지 말고 \"모르겠음\"이라고 답하세요.\n\n"
            + "\n".join(f"{i + 1}. {q}" for i, (q, _) in enumerate(questions)))


def client():
    # drawread.py 와 같은 방식
    if not os.environ.get("ANTHROPIC_API_KEY"):
        for line in Path.home().joinpath(".secrets/tokens.env").read_text(encoding="utf-8").splitlines():
            if line.startswith(("ANTHROPIC_API_KEY=", "CLAUDE_API_KEY=")):
                os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
    import anthropic
    return anthropic.Anthropic()


def text_of(msg):
    return next(b["text"] if isinstance(b, dict) else b.text for b in (msg["content"] if isinstance(msg, dict) else msg.content)
                if (b["type"] if isinstance(b, dict) else b.type) == "text")


def cards(page):
    pngs = sorted(CARDS.glob(f"{page}_*.png"), key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    assert pngs, f"out/cards/{page}_*.png 없음 — render_cards.py {page} 먼저"
    return pngs, [{"type": "image", "source": {"type": "base64", "media_type": "image/png",
                   "data": base64.standard_b64encode(p.read_bytes()).decode()}} for p in pngs]


def submit(page, out):
    questions, prompt = QUESTIONS[page], read_prompt(QUESTIONS[page])
    pngs, imgs = cards(page)
    reqs = [{"custom_id": f"{m}-{k}", "params": {
        "model": mid, "max_tokens": 16000,
        "output_config": {"effort": "medium", "format": {"type": "json_schema", "schema": READ_SCHEMA}},
        "messages": [{"role": "user", "content": imgs + [{"type": "text", "text": prompt}]}]}}
        for m, mid in MODELS.items() for k in range(N)]
    batch = client().messages.batches.create(requests=reqs)
    (out / "batch_id.txt").write_text(batch.id)
    (out / "meta.json").write_text(json.dumps({"cards": [p.name for p in pngs], "prompt": prompt, "questions": questions},
                                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(batch.id, len(reqs), "건,", len(pngs), "장")


def wait(page, out):
    c, bid = client(), (out / "batch_id.txt").read_text().strip()
    while (b := c.messages.batches.retrieve(bid)).processing_status != "ended":
        print(time.strftime("%H:%M:%S"), b.request_counts, flush=True)
        time.sleep(30)
    with open(out / "answers.jsonl", "w", encoding="utf-8") as f:
        for r in c.messages.batches.results(bid):
            f.write(r.to_json(indent=None) + "\n")
    print("ended", b.request_counts)


def grade(page, out):
    questions, c = QUESTIONS[page], client()
    rows = {}
    for line in open(out / "answers.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["result"]["type"] != "succeeded":
            print("실패", r["custom_id"], r["result"]); continue
        rows[r["custom_id"]] = {a["q"]: a["answer"] for a in json.loads(text_of(r["result"]["message"]))["answers"]}
    graded = {}
    log = open(out / "judge.jsonl", "w", encoding="utf-8")
    for cid, ans in sorted(rows.items()):
        g = {1: (ans.get(1, "").strip()[:1] == questions[0][1], "객관식 코드 채점")}
        body = "\n\n".join(f"{i}. 질문: {q}\n정답 기준: {key}\n답: {ans.get(i, '(없음)')}"
                           for i, (q, key) in enumerate(questions, 1) if i > 1)
        prompt = ("아래는 소개 영상을 본 사람의 답입니다. 각 답이 정답 기준의 핵심을 담고 있으면 correct=true, "
                  "빠졌거나 틀렸거나 '모르겠음'이면 false 입니다. 표현이 달라도 뜻이 같으면 맞습니다.\n\n" + body)
        msg = c.messages.create(model=MODELS["opus"], max_tokens=16000,
                                output_config={"effort": "medium", "format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
                                messages=[{"role": "user", "content": prompt}])
        log.write(json.dumps({"custom_id": cid, "prompt": prompt, "response": msg.to_dict()}, ensure_ascii=False) + "\n")
        for x in json.loads(text_of(msg))["grades"]:
            g[x["q"]] = (x["correct"], x["why"])
        graded[cid] = g
    head = ["| # | 질문 | " + " | ".join(MODELS) + " |", "| --- | --- | " + " | ".join("---" for _ in MODELS) + " |"]
    for i, (q, _) in enumerate(questions, 1):
        cells = [f"{sum(graded[k][i][0] for k in graded if k.startswith(m))}/{sum(1 for k in graded if k.startswith(m))}" for m in MODELS]
        head.append(f"| {i} | {q[:30]} | " + " | ".join(cells) + " |")
    head.append("\n## 틀린 답")
    for i, (q, key) in enumerate(questions, 1):
        wrong = [(k, rows[k].get(i, ""), graded[k][i][1]) for k in sorted(graded) if not graded[k][i][0]]
        if wrong:
            head.append(f"\n### {i}. {q}\n기준: {key}")
            head += [f"- {k}: {a}  — 채점: {w}" for k, a, w in wrong]
    (out / "report.md").write_text("\n".join(head), encoding="utf-8")
    print("\n".join(head))


def order(page, out):
    """1번 객관식 위치 편향 재확인. swap: 보기 1·2 바꿈(정답이 2번 자리로), why: 원순서 + 이유 한 문장."""
    q, key = QUESTIONS[page][0]
    head, opts = q.split(" 보기 중 하나의 번호만: ")
    texts = re.findall(r"\d\) (.+?)(?=  \d\)|$)", opts)
    assert key == "1" and len(texts) == 4, (key, texts)
    swapped = [texts[1], texts[0]] + texts[2:]
    variants = [("swap", swapped, "", "2"), ("why", texts, "\n번호를 고른 뒤 이유를 한 문장으로.", "1")]
    c, _imgs = client(), cards(page)[1]
    tally = {}
    with open(out / "q1_order.jsonl", "w", encoding="utf-8") as f:
        for name, ts, suffix, answer in variants:
            prompt = ("위 사진들은 인스타그램 릴스에서 넘겨 본 짧은 소개 영상의 장면들입니다(1번부터 순서대로).\n"
                      "당신은 이 분야 일을 해 본 적 없는 일반인입니다. 화면에 보이는 것만으로 답하세요.\n\n"
                      + head + "\n" + "  ".join(f"{i + 1}) {t}" for i, t in enumerate(ts)) + suffix)
            for k in range(N):
                msg = c.messages.create(model=MODELS["haiku"], max_tokens=4000, output_config={"effort": "medium"},
                                        messages=[{"role": "user", "content": _imgs + [{"type": "text", "text": prompt}]}])
                pick = (re.search(r"\d", text_of(msg)) or [""])[0]
                tally.setdefault(name, []).append(pick)
                f.write(json.dumps({"variant": name, "k": k, "answer": answer, "pick": pick, "prompt": prompt,
                                    "response": msg.to_dict()}, ensure_ascii=False) + "\n")
                print(name, k, "답", pick, "정답", answer, "O" if pick == answer else "X", flush=True)
    for name, picks in tally.items():
        print(name, "고른 번호:", picks)


if __name__ == "__main__":
    cmd, page = sys.argv[1], sys.argv[2]
    out = HERE / "out" / "quiz" / page
    out.mkdir(parents=True, exist_ok=True)
    {"submit": submit, "wait": wait, "grade": grade, "order": order}[cmd](page, out)

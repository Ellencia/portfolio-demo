"""바플(buyflow) 포폴용 데모 DB — 가상 회사·사업·거래처·품목으로 처음부터 만든다 (실제 DB 는 열지 않음).

가상 회사: 한결시스템 (키오스크·디지털 사이니지 설치). 담당자 김성진은 실명(본인 허락), 나머지는 가상.
실행: <바플 폴더>\\.venv\\Scripts\\python -X utf8 seed_demo.py  ->  bapl/data/buyflow.db (지우고 새로)
"""
import os
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
DB = DATA / "buyflow.db"
os.environ["BUYFLOW_DATA"] = str(DATA)  # 첨부·백업도 데모 폴더로 (실제 data 폴더 안 건드림)
os.environ["BUYFLOW_DB"] = str(DB)
sys.path.insert(0, str(HERE.resolve().parents[2] / "projects" / "buyflow"))  # 같은 작업 폴더의 바플

from buyflow import plans  # noqa: E402
from buyflow.db import connect, ensure_schema  # noqa: E402
from buyflow.orders import create_order  # noqa: E402
from buyflow.projects import create_project  # noqa: E402
from buyflow.purchases import create_purchase  # noqa: E402
from buyflow.stock import create_move  # noqa: E402

ME, MATE = "김성진", "이도윤"
# 품목: (이름, 규격, 단가, 거래처)
IT = {
    "touch32": ("32인치 터치 모니터", '32" FHD 정전식', 412_000, "새솔디스플레이"),
    "touch22": ("21.5인치 터치 모니터", '21.5" FHD 정전식', 268_000, "새솔디스플레이"),
    "sign43": ("43인치 사이니지 디스플레이", '43" 700nit 세로형', 735_000, "새솔디스플레이"),
    "minipc": ("미니 PC", "i5 / 8GB / SSD 256GB", 389_000, "오름컴퓨터"),
    "printer": ("영수증 프린터", "80mm 감열식", 142_000, "하늘프린텍"),
    "kiosk": ("키오스크 함체", "스탠드형 SPCC 분체도장", 520_000, "대성메탈"),
    "wall": ("벽부형 함체", "43인치용 SPCC", 310_000, "대성메탈"),
    "bracket": ("설치 브라켓", "VESA 200x200", 23_000, "대성메탈"),
    "acryl": ("아크릴 커버", "5T 투명 가공", 38_000, "맑은아크릴"),
    "hdmi": ("HDMI 케이블", "2.0 / 3m", 6_800, "미래케이블"),
    "lan": ("랜 케이블", "CAT6 / 5m", 4_200, "미래케이블"),
    "adapter": ("전원 어댑터", "12V 5A", 18_500, "바른전원"),
    "led": ("대기번호 표시기", "3열 LED 실내형", 186_000, "새솔디스플레이"),
}


def L(key, qty, **kw):
    name, spec, price, vendor = IT[key]
    return {"item_name": name, "spec": spec, "qty": str(qty), "unit_price": str(price), "vendor_name": vendor, **kw}


PROJECTS = [
    dict(code="P26-011", name="강변몰 무인 키오스크 12대", client_name="강변몰", contract_amount=186_000_000, budget=128_000_000,
         status="진행", start_date="2026-09-15", end_date="2026-11-20"),
    dict(code="P26-014", name="새봄병원 대기번호 표시기", client_name="새봄의료재단", contract_amount=64_000_000, budget=41_000_000,
         status="진행", start_date="2026-09-22", end_date="2026-11-10"),
    dict(code="P26-017", name="한빛도서관 안내 사이니지", client_name="한빛구청", contract_amount=92_000_000, budget=60_000_000,
         status="진행", start_date="2026-10-01", end_date="2026-12-15"),
    dict(code="P26-019", name="도담초 스마트 교실", client_name="도담교육지원청", contract_amount=48_000_000, budget=31_000_000,
         status="진행", start_date="2026-10-12", end_date="2026-12-30"),
]
PN = {p["code"]: p["name"] for p in PROJECTS}


def order(code, date, lines, due=None, mgr=ME, status="승인완료"):
    return create_order(str(DB), {"order_date": date, "due_date": due, "project_code": code, "project_name": PN[code],
                                  "manager_name": mgr, "status": status, "issuer": "한결시스템"}, lines)


def purchase(code, date, oid, lines, status, mgr=ME):
    return create_purchase(str(DB), {"buy_date": date, "project_code": code, "project_name": PN[code], "manager_name": mgr,
                                     "from_order_ids": str(oid), "status": status, "issuer": "한결시스템"}, lines)


def main():
    DATA.mkdir(exist_ok=True)
    for p in DATA.glob("buyflow.db*"):
        p.unlink()
    conn = connect(str(DB))
    ensure_schema(conn)
    conn.close()
    for p in PROJECTS:
        create_project(str(DB), {**p, "manager_name": ME})

    # 강변몰 키오스크 12대 — 대부분 진행, 프린터는 아직
    a = [L("touch32", 12), L("minipc", 12)]
    o1 = order("P26-011", "2026-09-29", [L("touch32", 12)], due="2026-10-10")
    o2 = order("P26-011", "2026-09-29", [L("minipc", 12)], due="2026-10-08")
    o3 = order("P26-011", "2026-10-02", [L("kiosk", 12)], due="2026-10-20")
    o4 = order("P26-011", "2026-10-06", [L("hdmi", 24), L("lan", 24)], due="2026-10-12")
    o5 = order("P26-011", "2026-10-21", [L("printer", 12)], due="2026-10-30", status="승인대기")
    p1 = purchase("P26-011", "2026-10-10", o1, [L("touch32", 12)], "정산")
    p2 = purchase("P26-011", "2026-10-08", o2, [L("minipc", 12)], "입고")
    purchase("P26-011", "2026-10-13", o4, [L("hdmi", 24), L("lan", 24)], "입고")
    purchase("P26-011", "2026-10-20", o3, [L("kiosk", 12)], "입고대기")
    create_move(str(DB), "in", {"move_date": "2026-10-10", "warehouse": "본사 창고", "manager_name": ME, "source_purchase_id": p1},
                [L("touch32", 12)])
    create_move(str(DB), "in", {"move_date": "2026-10-08", "warehouse": "본사 창고", "manager_name": ME, "source_purchase_id": p2},
                [L("minipc", 12)])
    create_move(str(DB), "out", {"move_date": "2026-10-22", "warehouse": "본사 창고", "manager_name": ME, "note": "강변몰 1차 설치"},
                [L("touch32", 6), L("minipc", 6)])

    # 새봄병원 — 표시기 납기 지남(아직 안 옴)
    o6 = order("P26-014", "2026-09-30", [L("led", 8)], due="2026-10-16")
    o7 = order("P26-014", "2026-10-05", [L("minipc", 2), L("adapter", 8)], due="2026-10-15", mgr=MATE)
    purchase("P26-014", "2026-10-15", o7, [L("minipc", 2), L("adapter", 8)], "입고", mgr=MATE)
    purchase("P26-014", "2026-10-14", o6, [L("led", 8)], "입고대기")

    # 한빛도서관 — 디스플레이 발주, 함체는 견적 중
    o8 = order("P26-017", "2026-10-14", [L("sign43", 6)], due="2026-11-04")
    o9 = order("P26-017", "2026-10-16", [L("minipc", 6), L("hdmi", 6)], due="2026-10-28", mgr=MATE)
    purchase("P26-017", "2026-10-23", o9, [L("minipc", 6), L("hdmi", 6)], "입고", mgr=MATE)

    # 도담초 — 막 시작
    o10 = order("P26-019", "2026-10-22", [L("touch22", 10)], due="2026-11-12")

    # 물량 줄 (사업별 필요 수량) — 발주서와 연결
    def plan(code, rows):
        ids = plans.add_lines_ids(str(DB), code, [
            {"item_name": IT[k][0], "spec": IT[k][1], "qty": q, "unit": u, "vendor_name": IT[k][3], "status": st,
             "quote_price": IT[k][2] if st in ("견적받음", "확정") else None} for k, q, u, st, _ in rows])
        for pid, (*_, oid) in zip(ids, rows):
            if oid:
                plans.link(str(DB), pid, oid, by=ME)

    plan("P26-011", [("touch32", 12, "대", "", o1), ("minipc", 12, "대", "", o2), ("kiosk", 12, "대", "", o3),
                     ("hdmi", 24, "개", "", o4), ("lan", 24, "개", "", o4), ("printer", 12, "대", "결재 대기", o5),
                     ("acryl", 12, "개", "견적요청", None), ("adapter", 14, "개", "미발주", None)])
    plan("P26-014", [("led", 8, "대", "", o6), ("minipc", 2, "대", "", o7), ("adapter", 8, "개", "", o7),
                     ("bracket", 8, "개", "확인 필요", None)])
    plan("P26-017", [("sign43", 6, "대", "", o8), ("minipc", 6, "대", "", o9), ("hdmi", 6, "개", "", o9),
                     ("wall", 6, "대", "견적받음", None), ("acryl", 6, "개", "견적요청", None)])
    plan("P26-019", [("touch22", 10, "대", "", o10), ("minipc", 10, "대", "미발주", None), ("bracket", 10, "개", "미발주", None)])

    # 진행 이력 (메신저 업무 봇이 넣는 소식) 몇 줄
    conn = connect(str(DB))
    # 매입 세금계산서 — 구매서와 짝이 맞은 것 3장 + 짝 없는 것 1장 (공급가액 = 구매서 합계)
    by_date = {r["buy_date"]: r["id"] for r in conn.execute("SELECT id, buy_date FROM purchase_header")}
    for no, (date, vendor, key, qty, buy_date) in enumerate((
            ("2026-10-10", "새솔디스플레이", "touch32", 12, "2026-10-10"),
            ("2026-10-08", "오름컴퓨터", "minipc", 12, "2026-10-08"),
            ("2026-10-15", "바른전원", "adapter", 8, None),
            ("2026-10-13", "미래케이블", "hdmi", 24, "2026-10-13")), 1):
        name, spec, price, _ = IT[key]
        sup = price * qty
        p = by_date.get(buy_date) if buy_date else None
        cur = conn.execute(
            "INSERT INTO tax_invoice (approval_no, issue_date, send_date, supplier_bizno, supplier_name, supplier_ceo, recipient_bizno,"
            " recipient_name, total_amount, supply_amount, vat_amount, category, type, issue_type, rep_item_name,"
            " matched_purchase_id, match_score, matched_at, imported_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f"2026{date[5:7]}{date[8:]}-4100000-{no:08d}", date, date, "000-00-00000", vendor, "(대표)", "000-00-00000",
             "한결시스템", sup + sup // 10, sup, sup // 10, "일반", "세금계산서", "정발행", name,
             p, 0.97 if p else None, f"{date}T18:00:00" if p else None, f"{date}T18:00:00"))
        conn.execute("INSERT INTO tax_invoice_line (invoice_id, line_no, item_date, item_name, spec, qty, unit_price, supply_amount, vat_amount)"
                     " VALUES (?,?,?,?,?,?,?,?,?)", (cur.lastrowid, 1, date, name, spec, qty, price, sup, sup // 10))
    _event(conn, o6, "2026-10-21 10:12", "업체 회신: LED 표시기 10/28 출고 예정")
    conn.commit()
    n = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
         for t in ("project", "order_header", "purchase_header", "stock_header", "plan_line", "vendor", "item")}
    conn.close()
    print(DB, n)


def _event(conn, oid, when, text):
    conn.execute("INSERT INTO doc_event (kind, ref_id, occurred_at, event_kind, summary, source, source_event_id, created_at) "
                 "VALUES ('order', ?, ?, 'task.progress', ?, 'work-inbox', ?, ?)", (oid, when, text, f"demo-{oid}-{when}", when))


# 포폴 이야기 단계 (capture.py 가 단계마다 화면을 찍음) — 강변몰 키오스크 함체 발주(3번) 한 건을 따라감
def news():
    """업체 소식이 메신저로 와서 발주서 진행 이력에 한 줄."""
    conn = connect(str(DB))
    _event(conn, 3, "2026-10-24 15:40", "업체 회신: 함체 도장 완료, 10/26 오전 배송")
    conn.commit()
    conn.close()


def arrive():
    """함체 도착 → 구매서 입고(입고 전표·흐름 기록 자동) + 아크릴 커버 견적 회신 → 물량 줄 견적받음."""
    from buyflow.purchases import set_purchase_status
    conn = connect(str(DB))
    pid = conn.execute("SELECT id FROM purchase_header WHERE from_order_ids = '3'").fetchone()[0]
    acryl = conn.execute("SELECT id FROM plan_line WHERE project_code = 'P26-011' AND item_name = ?", (IT["acryl"][0],)).fetchone()[0]
    conn.close()
    set_purchase_status(str(DB), pid, "입고", ME)
    plans.update_line(str(DB), acryl, {"status": "견적받음", "quote_price": IT["acryl"][2], "note": "견적서 메일 10/24"})


if __name__ == "__main__":
    {"news": news, "arrive": arrive}.get(sys.argv[1] if len(sys.argv) > 1 else "", main)()

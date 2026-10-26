| # | 질문 | opus | haiku |
| --- | --- | --- | --- |
| 1 | 이 영상이 소개하는 것은? 보기 중 하나의 번호만: 1 | 3/3 | 3/3 |
| 2 | 만든 사람은 왜 이 웹앱을 만들었어? | 3/3 | 2/3 |
| 3 | 업체가 메신저로 '내일 배송'이라고 말하면 어떻게 돼? | 3/3 | 3/3 |
| 4 | 물건이 도착해서 처리하면 화면에서 뭐가 바뀌어? | 3/3 | 3/3 |
| 5 | 견적서 메일이 오면 할 일은 어디서 어디로 옮겨 가? | 3/3 | 2/3 |
| 6 | 첫 화면은 뭘 대신 세 줘? | 3/3 | 3/3 |
| 7 | 이 앱은 회사 전산(ERP)과 어떤 관계야? | 3/3 | 3/3 |
| 8 | 이 앱은 누가 만들었고 지금 어떻게 쓰여? | 3/3 | 2/3 |

## 틀린 답

### 2. 만든 사람은 왜 이 웹앱을 만들었어?
기준: 주문한 물건이 지금 어디쯤 왔는지 회사 전산(ERP)으로는 알 수 없어서
- haiku-0: 화면에 이유가 직접 나오지는 않지만, 회사 전산에 적힌 주문·구매 정보를 여러 화면을 오가며 찾는 번거로움을 줄이려는 것으로 보임. 다만 명확히 알 수는 없음  — 채점: The answer guesses the reason was reducing the hassle of switching screens. It misses the core reason in the criterion: the ERP could not show where an ordered item currently is.

### 5. 견적서 메일이 오면 할 일은 어디서 어디로 옮겨 가?
기준: '견적 기다리는 것'에서 '발주(주문) 넣을 것'으로
- haiku-2: '발주 넣을 것' 목록에서 '견적 기다리는 것' 목록으로 옮겨 감. 견적서 메일을 받으면 '주문 넣을 차례'로 넘어간다는 흐름으로 보임  — 채점: 옮겨 가는 방향을 '발주 넣을 것'에서 '견적 기다리는 것'으로 거꾸로 적음. 뒤 문장과도 앞뒤가 맞지 않음.

### 8. 이 앱은 누가 만들었고 지금 어떻게 쓰여?
기준: 혼자 만들어 매일 쓰는 중(실제 운영)
- haiku-0: 화면에 만든 사람 정보는 없음. 사내 PC 서버에 Python, FastAPI, SQLite로 만든 것으로 나오며, 30분마다 가져와 대조하고 매일 쓰는 것으로 보임. 누가 만들었는지는 모르겠음  — 채점: The answer mentions daily use but says it doesn't know who made it, so it misses the core point that one person built it alone.
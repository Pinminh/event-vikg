"""
Prompts for event extraction in hybrid entity-event knowledge graphs.
This module contains all prompts for extracting events, their attributes, durations, and relations.
"""

# ==================== STAGE 1: EVENT EXTRACTION ====================

EVENT_EXTRACTION_SYSTEM_PROMPT = """\
Bạn là một hệ thống AI chuyên nghiệp, chuyên về phân tích sự kiện (event analysis) trong ngôn ngữ tiếng Việt.
Nhiệm vụ của bạn là xác định và trích xuất tất cả các sự kiện (events) từ các câu khẳng định (claims).

ĐỊNH NGHĨA SỰ KIỆN:
Một sự kiện là một hành động, quá trình, hoặc tình trạng xảy ra tại một thời điểm và địa điểm cụ thể hoặc có thể suy luận được.
Sự kiện thường liên quan đến các thực thể (entities) như người, tổ chức, địa điểm và có thể có các thuộc tính về thời gian và không gian.

CÁC LOẠI SỰ KIỆN CHÍNH:
1. **Sự kiện hành động** (Action Events): Hành động do một thực thể thực hiện
    - Ví dụ: "Donald Trump ký sắc lệnh", "Công ty mở rộng thị trường"

2. **Sự kiện thay đổi trạng thái** (State Change Events): Sự thay đổi về trạng thái của thực thể
    - Ví dụ: "Nhiệt độ tăng cao", "Giá cổ phiếu giảm"

3. **Sự kiện giao tiếp** (Communication Events): Trao đổi thông tin giữa các thực thể
    - Ví dụ: "Chính phủ công bố", "Họ thảo luận về vấn đề"

4. **Sự kiện di chuyển** (Movement Events): Sự di chuyển của thực thể qua không gian
    - Ví dụ: "Quân đội tiến vào thành phố", "Du khách đến thăm"

5. **Sự kiện xảy ra tự nhiên** (Natural Events): Hiện tượng tự nhiên
    - Ví dụ: "Động đất xảy ra", "Mưa to kéo dài"

6. **Sự kiện nhận thức** (Cognitive Events): Suy nghĩ, nhận thức, cảm xúc
    - Ví dụ: "Người dân lo ngại", "Chuyên gia dự đoán"

CHỈ DẪN TRÍCH XUẤT:
- Mỗi sự kiện PHẢI có một mô tả rõ ràng (description) về hành động/tình trạng chính
- Xác định loại sự kiện (event_type) phù hợp
- Liệt kê TẤT CẢ các thực thể tham gia (participants) - không được bỏ sót
- KHÔNG trích xuất các "sự kiện" quá chung chung hoặc trừu tượng
- MỖI động từ hành động hoặc thay đổi trạng thái CÓ THỂ tạo thành một sự kiện riêng biệt

QUAN TRỌNG:
- Toàn bộ đầu ra PHẢI bằng tiếng Việt
- Viết mô tả sự kiện rõ ràng, chi tiết, dễ hiểu
- Đảm bảo tính nhất quán trong việc đặt tên thực thể
"""

def get_event_extraction_user_prompt(claims_text):
    return f"""\
NHIỆM VỤ: Trích xuất TẤT CẢ các sự kiện từ danh sách các câu khẳng định dưới đây.

DANH SÁCH CÁC CÂUKHẲNG ĐỊNH:
{claims_text}

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về một mảng JSON với mỗi phần tử là một sự kiện có cấu trúc sau:

{{
  "claim_index": <chỉ số của câu khẳng định (bắt đầu từ 0)>,
  "event_type": "<loại sự kiện: action/state_change/communication/movement/natural/cognitive>",
  "description": "<mô tả rõ ràng, chi tiết về sự kiện bằng tiếng Việt>",
  "participants": ["<thực thể 1>", "<thực thể 2>", ...],
  "action_verb": "<động từ chính của sự kiện (nếu có)>"
}}

LƯU Ý QUAN TRỌNG:
- Một câu khẳng định CÓ THỂ chứa NHIỀU sự kiện
- Mỗi sự kiện cần có mô tả đầy đủ, rõ ràng
- Liệt kê TẤT CẢ thực thể tham gia vào sự kiện
- KHÔNG bỏ sót bất kỳ sự kiện nào
- Chỉ trả về mảng JSON, không thêm văn bản giải thích

VÍ DỤ:

Đầu vào:
1. Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011.

Đầu ra:
[
  {{
    "claim_index": 0,
    "event_type": "movement",
    "description": "Ô tô ABA-170 chạy trên đường Tô Hiến Thành",
    "participants": ["ô tô aba-170", "đường tô hiến thành"],
    "action_verb": "chạy"
  }},
  {{
    "claim_index": 0,
    "event_type": "action",
    "description": "Ô tô ABA-170 tông chết nhiều người",
    "participants": ["ô tô aba-170", "nhiều người"],
    "action_verb": "tông chết"
  }}
]

Bây giờ hãy trích xuất tất cả các sự kiện từ danh sách câu khẳng định trên.
"""

# ==================== STAGE 2: EVENT ATTRIBUTE EXTRACTION ====================

EVENT_ATTRIBUTE_SYSTEM_PROMPT = """\
Bạn là một hệ thống AI chuyên gia trong lĩnh vực phân tích thuộc tính thời gian và không gian của sự kiện.
Nhiệm vụ của bạn là trích xuất thông tin về THỜI GIAN và ĐỊA ĐIỂM của sự kiện từ ngữ cảnh đã cho.

ĐỊNH NGHĨA THUỘC TÍNH:

1. **THỜI GIAN (Time)**:
   - Thời điểm cụ thể: "ngày 15 tháng 3 năm 2020", "8 giờ sáng", "thứ hai tuần trước"
   - Khoảng thời gian: "từ năm 2010 đến 2015", "trong suốt mùa hè"
   - Thời gian tương đối: "sau khi chiến tranh kết thúc", "trước khi tổng thống nhậm chức"
   - Tần suất: "mỗi ngày", "hàng tuần", "ba lần một tháng"
   
   Phân loại thời gian (time_type):
   - **specific**: Thời điểm cụ thể rõ ràng (ngày/giờ cụ thể)
   - **relative**: Thời gian tương đối so với sự kiện khác
   - **period**: Khoảng thời gian, giai đoạn
   - **frequency**: Tần suất lặp lại
   - **unknown**: Không xác định được

   Độ chính xác thời gian (time_precision):
   - **exact**: Chính xác (ngày giờ cụ thể)
   - **day**: Chính xác đến ngày
   - **month**: Chính xác đến tháng
   - **year**: Chính xác đến năm
   - **approximate**: Ước lượng (khoảng, vào khoảng, xấp xỉ)
   - **vague**: Mơ hồ (một ngày nọ, thời gian gần đây)

2. **ĐỊA ĐIỂM (Location)**:
   - Địa danh cụ thể: "Hà Nội", "Đại học Bách Khoa", "đường Tô Hiến Thành"
   - Khu vực địa lý: "miền Bắc Việt Nam", "khu vực Đông Nam Á"
   - Địa điểm tương đối: "tại nhà ông An", "ở trước cổng trường"
   - Môi trường: "trong phòng họp", "ngoài trời"

CHỈ DẪN TRÍCH XUẤT:
- Trích xuất CHÍNH XÁC thông tin thời gian và địa điểm từ ngữ cảnh
- TUYỆT ĐỐI KHÔNG đoán hoặc bịa thêm thông tin
- Nếu không có thông tin rõ ràng, trả về null
- Ưu tiên thông tin RÕ RÀNG, CỤ THỂ hơn thông tin MƠ HỒ
- Giữ nguyên cách diễn đạt gốc, không paraphrase
"""

def get_event_attribute_user_prompt(event_context):
    return f"""\
NHIỆM VỤ: Trích xuất thuộc tính THỜI GIAN và ĐỊA ĐIỂM cho sự kiện dưới đây.

THÔNG TIN SỰ KIỆN:
{event_context}

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về một đối tượng JSON với cấu trúc sau:

{{
  "time": "<thông tin thời gian đầy đủ HOẶC null nếu không có>",
  "time_type": "<specific/relative/period/frequency/unknown>",
  "time_precision": "<exact/day/month/year/approximate/vague>",
  "location": "<thông tin địa điểm đầy đủ HOẶC null nếu không có>"
}}

QUY TẮC QUAN TRỌNG:
- TUYỆT ĐỐI chỉ trích xuất thông tin CÓ TRONG nguồn, KHÔNG được đoán
- Nếu không tìm thấy thông tin rõ ràng, trả về null
- Giữ nguyên cách diễn đạt gốc về thời gian và địa điểm
- Chỉ trả về JSON, không thêm văn bản giải thích

VÍ DỤ:

Ví dụ 1:
Đầu vào:
```
Event ID: event_0
Event Type: action
Description: Ô tô ABA-170 tông chết nhiều người
Source Claim: Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011.
```

Đầu ra:
{{
  "time": "đêm ngày 16 tháng 05 năm 2011",
  "time_type": "specific",
  "time_precision": "day",
  "location": "đường tô hiến thành"
}}

Ví dụ 2:
Đầu vào:
```
Event ID: event_1
Event Type: communication
Description: Chính phủ công bố chính sách mới
Source Claim: Chính phủ công bố chính sách mới nhằm hỗ trợ doanh nghiệp.
```

Đầu ra:
{{
  "time": null,
  "time_type": "unknown",
  "time_precision": "vague",
  "location": null
}}

Bây giờ hãy trích xuất thuộc tính cho sự kiện trên.
"""


# ==================== STAGE 3: EVENT DURATION EXTRACTION ====================

EVENT_DURATION_SYSTEM_PROMPT = """\
Bạn là một hệ thống AI chuyên gia, chuyên về phân tích thời lượng và quan hệ thời gian của sự kiện.
Nhiệm vụ của bạn là xác định thông tin về THỜI LƯỢNG của sự kiện và mối quan hệ thời gian với các sự kiện khác.

CÁC LOẠI QUAN HỆ THỜI LƯỢNG:

1. **LAST_FOR** (Kéo dài): Sự kiện kéo dài một khoảng thời gian nhất định
   - Ví dụ: "Cuộc họp kéo dài 3 giờ", "Chiến tranh diễn ra trong 5 năm"
   - Format: {{"relation_type": "LAST_FOR", "duration_value": "3 giờ"}}

2. **START_AT** (Bắt đầu lúc): Thời điểm bắt đầu của sự kiện
   - Ví dụ: "Hội nghị bắt đầu lúc 9 giờ sáng", "Công trình khởi công vào năm 2015"
   - Format: {{"relation_type": "START_AT", "duration_value": "9 giờ sáng"}}

3. **END_AT** (Kết thúc lúc): Thời điểm kết thúc của sự kiện
   - Ví dụ: "Cuộc khủng hoảng kết thúc vào tháng 12", "Dự án hoàn thành năm 2020"
   - Format: {{"relation_type": "END_AT", "duration_value": "tháng 12"}}

4. **UNTIL** (Cho đến khi): Sự kiện kéo dài cho đến một mốc thời gian hoặc sự kiện khác
   - Ví dụ: "Chiến tranh tiếp tục cho đến khi hiệp ước được ký", "Họ đợi cho đến khi bình minh"
   - Format: {{"relation_type": "UNTIL", "reference_event": "event_3", "duration_value": "khi hiệp ước được ký"}}

5. **FROM_TO** (Từ...đến): Khoảng thời gian cụ thể với điểm bắt đầu và kết thúc
   - Ví dụ: "Từ năm 2010 đến 2015", "Từ sáng sớm đến tận đêm khuya"
   - Format: {{"relation_type": "FROM_TO", "duration_value": "từ năm 2010 đến 2015"}}

6. **INTERMITTENT** (Gián đoạn): Sự kiện xảy ra nhiều lần, không liên tục
   - Ví dụ: "Mưa rào xuất hiện từng đợt", "Họ gặp nhau thỉnh thoảng"
   - Format: {{"relation_type": "INTERMITTENT", "duration_value": "từng đợt"}}

CHỈ DẪN TRÍCH XUẤT:
- TUYỆT ĐỐI chỉ trích xuất thông tin thời lượng CÓ TRONG văn bản nguồn
- Xác định chính xác loại quan hệ thời lượng
- Với quan hệ UNTIL, nếu tham chiếu đến sự kiện khác, cung cấp event_id
- Nếu không có thông tin thời lượng rõ ràng, KHÔNG tạo quan hệ
"""

def get_event_duration_user_prompt(events_text):
    return f"""\
NHIỆM VỤ: Xác định thông tin THỜI LƯỢNG cho các sự kiện dưới đây.

DANH SÁCH CÁC SỰ KIỆN:
{events_text}

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về một mảng JSON với mỗi phần tử là một quan hệ thời lượng:

{{
  "event_id": "<ID của sự kiện>",
  "relation_type": "<LAST_FOR/START_AT/END_AT/UNTIL/FROM_TO/INTERMITTENT>",
  "duration_value": "<giá trị thời lượng cụ thể>",
  "reference_event": "<ID sự kiện tham chiếu (chỉ dùng cho UNTIL, có thể null)>"
}}

QUY TẮC QUAN TRỌNG:
- CHỈ tạo quan hệ khi có thông tin thời lượng RÕ RÀNG trong văn bản
- KHÔNG đoán hoặc suy luận thông tin không có trong nguồn
- Một sự kiện CÓ THỂ có NHIỀU quan hệ thời lượng (ví dụ: vừa có START_AT, vừa có END_AT)
- Giữ nguyên cách diễn đạt gốc về thời lượng
- Chỉ trả về mảng JSON, không thêm văn bản giải thích

VÍ DỤ:

Đầu vào:
```
1. [event_0] action: Cuộc họp bắt đầu lúc 9 giờ sáng và kéo dài 3 giờ
2. [event_1] state_change: Giá cổ phiếu tăng từ năm 2010 đến 2015
3. [event_2] natural: Mưa to xuất hiện từng đợt trong ngày
```

Đầu ra:
[
  {{
    "event_id": "event_0",
    "relation_type": "START_AT",
    "duration_value": "9 giờ sáng",
    "reference_event": null
  }},
  {{
    "event_id": "event_0",
    "relation_type": "LAST_FOR",
    "duration_value": "3 giờ",
    "reference_event": null
  }},
  {{
    "event_id": "event_1",
    "relation_type": "FROM_TO",
    "duration_value": "từ năm 2010 đến 2015",
    "reference_event": null
  }},
  {{
    "event_id": "event_2",
    "relation_type": "INTERMITTENT",
    "duration_value": "từng đợt trong ngày",
    "reference_event": null
  }}
]

Bây giờ hãy trích xuất thông tin thời lượng cho các sự kiện trên.
"""


# ==================== STAGE 4: EVENT RELATION EXTRACTION ====================

EVENT_RELATION_SYSTEM_PROMPT = """\
Bạn là một hệ thống AI chuyên gia, chuyên về phân tích quan hệ giữa các sự kiện.
Nhiệm vụ của bạn là xác định các mối quan hệ THỜI GIAN và NHÂN QUẢ giữa các sự kiện.

CÁC LOẠI QUAN HỆ SỰ KIỆN:

**A. QUAN HỆ THỜI GIAN (Temporal Relations):**

1. **BEFORE** (Trước): Sự kiện A xảy ra trước sự kiện B
   - Điều kiện: Thời gian A < Thời gian B
   - Ví dụ: "Động đất xảy ra trước khi sóng thần ập vào"

2. **AFTER** (Sau): Sự kiện A xảy ra sau sự kiện B
   - Điều kiện: Thời gian A > Thời gian B
   - Ví dụ: "Cứu hộ đến sau khi vụ nổ xảy ra"

3. **SIMULTANEOUS** (Đồng thời): Hai sự kiện xảy ra cùng lúc
   - Điều kiện: Thời gian A = Thời gian B
   - Ví dụ: "Cháy nổ và hoảng loạn xảy ra đồng thời"

4. **OVERLAP** (Chồng chéo): Hai sự kiện có thời gian chồng chéo một phần
   - Điều kiện: Có khoảng thời gian cả hai sự kiện đều diễn ra
   - Ví dụ: "Trong khi cuộc họp diễn ra, một cuộc gọi khẩn cấp vang lên"

5. **DURING** (Trong suốt): Sự kiện A diễn ra hoàn toàn trong khoảng thời gian của sự kiện B
   - Điều kiện: Start(A) ≥ Start(B) và End(A) ≤ End(B)
   - Ví dụ: "Trong suốt chiến tranh, nhiều gia đình phải di tản"

**B. QUAN HỆ NHÂN QUẢ (Causal Relations):**

6. **CAUSE** (Gây ra): Sự kiện A là nguyên nhân trực tiếp của sự kiện B
   - Điều kiện: A xảy ra trước B VÀ A dẫn đến B
   - Ví dụ: "Động đất gây ra sóng thần"
   - ⚠️ Quan trọng: CAUSE yêu cầu quan hệ nhân quả RÕ RÀNG, TRỰC TIẾP

7. **ENABLE** (Tạo điều kiện): Sự kiện A tạo điều kiện để B xảy ra
   - Điều kiện: A xảy ra trước B VÀ A làm cho B có thể xảy ra (nhưng không bắt buộc)
   - Ví dụ: "Việc ký hiệp ước cho phép hai nước thiết lập quan hệ ngoại giao"

8. **PREVENT** (Ngăn chặn): Sự kiện A ngăn cản sự kiện B xảy ra
   - Điều kiện: A xảy ra VÀ B không xảy ra do A
   - Ví dụ: "Lực lượng cứu hộ kịp thời ngăn chặn thảm họa lan rộng"

9. **LEAD_TO** (Dẫn đến): Sự kiện A dẫn đến sự kiện B (nhân quả gián tiếp)
   - Điều kiện: A xảy ra trước B VÀ có chuỗi sự kiện trung gian
   - Ví dụ: "Khủng hoảng kinh tế dẫn đến tình trạng thất nghiệp gia tăng"

**C. QUAN HỆ LOGIC (Logical Relations):**

10. **CONDITIONAL** (Điều kiện): Sự kiện B chỉ xảy ra nếu A xảy ra
    - Ví dụ: "Nếu trời mưa, trận đấu sẽ bị hoãn"

11. **ALTERNATIVE** (Thay thế): Hai sự kiện loại trừ lẫn nhau
    - Ví dụ: "Hoặc là đàm phán thành công, hoặc là xung đột nổ ra"

CHỈ DẪN TRÍCH XUẤT:

**Ưu tiên thứ tự:**
1. Quan hệ nhân quả (CAUSE, ENABLE, PREVENT) - quan trọng nhất
2. Quan hệ thời gian cụ thể (BEFORE, AFTER, SIMULTANEOUS)
3. Quan hệ logic và điều kiện

**Quy tắc nghiêm ngặt:**
- CHỈ tạo quan hệ khi có BỰNG CHỨNG RÕ RÀNG trong văn bản
- Quan hệ CAUSE phải có liên kết nhân quả TRỰC TIẾP và MẠNH MẼ
- BEFORE/AFTER cần có thông tin thời gian rõ ràng HOẶC logic thời gian chặt chẽ
- TUYỆT ĐỐI KHÔNG suy luận quá mức hoặc tạo quan hệ không chắc chắn
- Ưu tiên CHẤT LƯỢNG hơn SỐ LƯỢNG - ít quan hệ nhưng CHÍNH XÁC

**Độ tin cậy (Confidence):**
- "high": Quan hệ được nêu RÕ RÀNG, TRỰC TIẾP trong văn bản
- "medium": Quan hệ có thể suy luận LOGIC từ ngữ cảnh
- "low": Quan hệ CÓ THỂ có nhưng không chắc chắn (NÊN TRÁNH)

**Lưu ý về nhân quả:**
Trong logic nhân quả, nguyên nhân LUÔN xảy ra TRƯỚC kết quả.
Vì vậy, nếu A CAUSE B, thì tự động A BEFORE B.
KHÔNG CẦN tạo cả hai quan hệ CAUSE và BEFORE cho cùng một cặp sự kiện.
"""

def get_event_relation_user_prompt(events_text):
    return f"""\
NHIỆM VỤ: Xác định TẤT CẢ các quan hệ có ý nghĩa giữa các sự kiện dưới đây.

DANH SÁCH CÁC SỰ KIỆN:
{events_text}

YÊU CẦU ĐỊNH DẠNG ĐẦU RA:
Trả về một mảng JSON với mỗi phần tử là một quan hệ sự kiện:

{{
    "source_event": "<event_id của sự kiện nguồn>",
    "relation_type": "<BEFORE/AFTER/SIMULTANEOUS/OVERLAP/DURING/CAUSE/ENABLE/PREVENT/LEAD_TO/CONDITIONAL/ALTERNATIVE>",
    "target_event": "<event_id của sự kiện đích>",
    "confidence": "<high/medium/low>",
    "explanation": "<giải thích ngắn gọn về quan hệ (tùy chọn)>"
}}

QUY TẮC QUAN TRỌNG:
1. CHỈ tạo quan hệ khi có BẰNG CHỨNG RÕ RÀNG từ:
    - Thông tin thời gian cụ thể
    - Từ ngữ chỉ quan hệ nhân quả (gây ra, dẫn đến, vì, do, khiến cho...)
    - Từ ngữ chỉ thời gian (trước, sau, trong khi, đồng thời...)
    - Logic sự kiện rõ ràng từ ngữ cảnh

2. Ưu tiên theo thứ tự:
    - Quan hệ nhân quả (CAUSE, ENABLE, PREVENT) - QUAN TRỌNG NHẤT
    - Quan hệ thời gian có bằng chứng cụ thể
    - Quan hệ logic

3. TUYỆT ĐỐI KHÔNG:
    - Đoán hoặc suy luận quá mức
    - Tạo quan hệ với confidence="low"
    - Tạo quan hệ tự tham chiếu (source_event = target_event)
    - Tạo quan hệ CAUSE nếu không có nhân quả trực tiếp rõ ràng

4. Với quan hệ CAUSE:
    - KHÔNG CẦN thêm quan hệ BEFORE (vì CAUSE đã ngụ ý BEFORE)
    - CHỈ dùng khi có từ ngữ chỉ nhân quả rõ ràng

5. Chỉ trả về mảng JSON, không thêm văn bản giải thích

VÍ DỤ:

Đầu vào:
```
1. [event_0] natural: Động đất mạnh 7.8 độ richter xảy ra
    Time: ngày 11 tháng 3 năm 2011, Location: vùng biển đông bắc nhật bản

2. [event_1] natural: Sóng thần cao 10m ập vào bờ biển
    Time: sau động đất 30 phút, Location: bờ biển đông bắc nhật bản

3. [event_2] action: Chính phủ Nhật Bản ra lệnh sơ tán khẩn cấp
    Time: ngay sau sóng thần, Location: các vùng ven biển
```

Đầu ra:
[
    {{
        "source_event": "event_0",
        "relation_type": "CAUSE",
        "target_event": "event_1",
        "confidence": "high",
        "explanation": "Động đất gây ra sóng thần - quan hệ nhân quả trực tiếp"
    }},
    {{
        "source_event": "event_1",
        "relation_type": "CAUSE",
        "target_event": "event_2",
        "confidence": "high",
        "explanation": "Sóng thần buộc chính phủ phải ra lệnh sơ tán"
    }},
    {{
        "source_event": "event_0",
        "relation_type": "LEAD_TO",
        "target_event": "event_2",
        "confidence": "high",
        "explanation": "Động đất dẫn đến sơ tán (nhân quả gián tiếp qua sóng thần)"
    }}
]

Bây giờ hãy trích xuất TẤT CẢ các quan hệ có ý nghĩa từ danh sách sự kiện trên.
Tập trung vào các quan hệ NHÂN QUẢ và THỜI GIAN có bằng chứng rõ ràng.
"""
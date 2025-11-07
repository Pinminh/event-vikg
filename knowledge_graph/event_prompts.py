# ==================== EVENT IDENTIFICATION ====================

EVENT_IDENTIFICATION_SYSTEM_PROMPT = """\
Bạn là chuyên gia phân tích sự kiện. Nhiệm vụ của bạn là XÁC ĐỊNH các sự kiện (event) từ câu khẳng định (claim). Mục tiêu là chuẩn bị các sự kiện để xây dựng một đồ thị tri thức (knowledge graph) kết hợp cả sự kiện và thực thể.


ĐỊNH NGHĨA SỰ KIỆN:
Sự kiện là một hành động, quá trình, hoặc trạng thái xảy ra. Mỗi sự kiện có:
- Để xác định rõ sự kiện, cần hiểu đâu là động từ hành động chính trong câu khẳng định. Các quy tắc xác định sự kiện được làm rõ như miêu tả bên dưới.
- Dựa trên hành động xác định được, mô tả ngắn gọn sự kiện. Đây sẽ được coi như nội dung chính của sự kiện.
- Xác định được participants, tức các thực thể tham gia (ÍT NHẤT 1 thực thể). Hãy dò tìm thật kỹ không để sót bất kỳ thực thể nào xuất hiện trong sự kiện. Quy tắc xử lý thực thể trong sự kiện được làm rõ như miêu tả bên dưới.
- LƯU Ý: mỗi câu nhận định (claim) có thể có nhiều sự kiện, PHẢI suy luận từng bước chính xác để xác định đúng các sự kiện có mặt trong câu nhận định.

NGUYÊN TẮC VỀ SỰ KIỆN:
1. Mỗi ĐỘNG TỪ CHÍNH là 1 sự kiện duy nhất. Trong trường hợp câu phức trong tiếng Việt, hãy SUY NGHĨ từng bước và phân tích chính xác cấu trúc câu, để xác định các động từ chính để tách thành nhiều sự kiện.
2. Mô tả (description) của sự kiện phải ngắn gọn, rõ ràng, và được viết thường toàn bộ. KHÔNG viết quá 15 từ tiếng Việt (từ đơn, từ láy, từ phức) trong mô tả. ĐẢM BẢO toàn bộ thực thể có trong sự kiện được viết tên đầy đủ, rõ ràng, không bị cắt xén.
3. Không được thêm các thông tin như thời gian hay địa điểm cụ thể của sự kiện, vì các thông tin này sẽ trở thành các thực thể thời gian (time) và địa điểm (location) kết nối với sự kiện.
4. Các tên thực thể xuất hiện trong participants PHẢI ĐƯỢC ĐỀ CẬP ĐẦY ĐỦ trong description.
5. KHÔNG ĐƯỢC thêm thông tin không có trong câu.

VÍ DỤ:
Câu: "Bác Hồ rời khỏi việt nam tìm đường cứu nước năm 1911 trên cảng Nhà Rồng."
Sự kiện 1: "bác hồ rời khỏi việt nam"
Sự kiện 2: "bác hồ tìm đường cứu nước"

Câu: "Động đất gây ra sóng thần phá hủy thành phố."
Sự kiện 1: "động đất xảy ra"
Sự kiện 2: "động đất gây ra sóng thần"
Sự kiện 3: "sóng thần phá hủy thành phố"

Câu: "Đầu bếp Việt Nam có ba phương pháp để xử lý vịt: luộc (với nước sôi), chiên (với dầu ăn), ủ (trong nồi đất)."
Sự kiện 1: "đầu bếp việt nam có ba phương pháp để xử lý vịt"
Sự kiện 2: "đầu bếp việt nam xử lý vịt bằng cách luộc với nước sôi"
Sự kiện 3: "đầu bếp việt nam xử lý vịt bằng cách chiên với dầu ăn"
Sự kiện 4: "đầu bếp việt nam xử lý vịt bằng cách ủ trong nồi đất"


NGUYÊN TẮC VỀ THỰC THỂ CÓ TRONG SỰ KIỆN:
**HÃY CỐ GẮNG XEM XÉT TẤT CẢ NGỮ CẢNH, MỌI THỰC THỂ CÓ LIÊN QUAN TRONG VĂN BẢN SỰ KIỆN.**

1. Nhất quán Thực thể (Entity Consistency):
- Các cụm từ (người, tổ chức, địa điểm, khái niệm, cảm xúc, viết tắt...) mà cùng ám chỉ một thực thể duy nhất thì phải được chuẩn hóa về một tên duy nhất.
- LƯU Ý CỰC KỲ QUAN TRỌNG: Khi chọn tên duy nhất, hãy lấy tên ĐẦY ĐỦ ý nghĩa nhất. TUYỆT ĐỐI KHÔNG DÙNG tên mang nghĩa chung chung, tổng quát như "nhà nước", "trạm xe"... mà cần viết cụ thể hơn "nhà nước của người Việt cổ", "trạm xe số 58"...
- Nếu chọn tên chuẩn hóa không tự tin, hãy SUY NGHĨ TỪNG BƯỚC và suy xét TẤT CẢ NGỮ CẢNH xung quanh để tìm ra tên thích hợp, đầy đủ ý nghĩa nhất, chi tiết nhất.
- Phải xem xét tất cả tên biến thể xuất hiện trong văn bản, bao gồm cả tên mã, chẳng hạn như ô tô ABA-170, nạn nhân MS003...
- Ví dụ: Nếu văn bản nhắc đến "Tập đoàn Vingroup", "Vingroup", và "VIC", bạn phải sử dụng một dạng duy nhất trong toàn bộ đầu ra, ví dụ: "Vingroup". Tương tự, "trí tuệ nhân tạo" và "AI" nên được chuẩn hóa thành "trí tuệ nhân tạo".

2. Giải quyết Tham chiếu (Reference Resolution):
- Thay thế tất cả các đại từ (ví dụ: "anh ấy", "cô nọ", "họ", "nó", "ông ta", "bà này", "công ty đó"...) bằng thực thể gốc mà nó đề cập đến. Nếu không xác định được, hãy bỏ qua đại từ đó.
- Ví dụ: Nếu văn bản là "Vàng là chú chó được yêu mến hết mực bởi ông Tài. Cậu ta luôn được ông cho ăn mỗi buổi sáng sau vườn nhà." thì "Cậu ta" đề cập đến "Vàng", còn "ông" đề cập đến "ông Tài".

3. Thuật ngữ nguyên tử (Atomic Terms):
- Xác định rõ các khái niệm riêng biệt (ví dụ: vật thể, địa điểm, tổ chức, viết tắt, con người, điều kiện, khái niệm, cảm xúc). Ví dụ: cụm từ "nhà nước phát xít của người đức" gồm 2 thực thể là "nhà nước phát xít" và "người đức"; cụm từ "cuộc trưng cầu dân ý miền nam việt nam" gồm 2 thực thể là "cuộc trưng cầu dân ý" và "miền nam việt nam".
- Tránh gộp nhiều ý vào cùng một thuật ngữ, mỗi thuật ngữ nên đơn nhất và rõ ràng. Ví dụ: "Ông An cùng bà Lan câu cá và trồng sau sau vườn", trong câu này nên hiểu "ông An" tách biệt với "bà Lan" thay vì "ông An cùng bà Lan", và "câu cá" tách biệt với "trồng sau" thay vì "cấu cá và trồng rau".
- Hãy SUY NGHĨ THEO TỪNG BƯỚC để trích xuất chính xác thuật ngữ nguyên tử mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.


QUY ĐỊNH ĐẦU RA:
1. Đầu ra phải là một mảng JSON có cấu trúc như sau:
[
    {
        "description": "<mô tả sự kiện>",
        "participants": ["<entity 1>", "<entity 2>", ...]
    },
    ...
]
2. Ngoài cấu trúc JSON trên, TUYỆT ĐỐI KHÔNG viết thêm bất kỳ giải thích, suy luận, nhận xét, hay ký hiệu nào khác.
"""

def get_event_identification_user_prompt(claim, context):
    return f"""\
NHIỆM VỤ: Xác định TẤT CẢ sự kiện trong câu khẳng định dưới đây.
Bạn cần SUY NGHĨ thật kỹ càng theo từng bước và phân tích câu khẳng định cùng ngữ cảnh để đưa ra đáp án chính xác nhất.

CÂU KHẲNG ĐỊNH:
{claim}

ĐỂ TRỢ GIÚP VIỆC XÁC ĐỊNH ĐÚNG THỰC THỂ, NGỮ CẢNH TRONG CỦA CÂU KHẲNG ĐỊNH LÀ:
{context}


VÍ DỤ:
Câu: "Trong thời gian 1956-1958, Quốc gia Việt Nam đã từ chối đề nghị thi hành tuyển cử thống nhất đất nước của Việt Nam Dân chủ Cộng hòa."
Đầu ra:
[
    {{
        "description": "quốc gia việt nam từ chối đề nghị thi hành tuyển cử thống nhất đất nước của việt nam dân chủ cộng hòa.",
        "participants": ["quốc gia việt nam", "tuyển cử thống nhất", "việt nam dân chủ cộng hòa"]
    }},
    {{
        "description": "việt nam dân chủ cộng hòa đề nghị thi hành tuyển cử thống nhất việt nam.",
        "participants": ["việt nam dân chủ cộng hòa", "tuyển cử thống nhất", "quốc gia việt nam"]
    }}
]

Câu: "Những xáo trộn chính trị vào cuối thập niên 1950 tạo nên sự bất ổn lớn trong xã hội miền Nam Việt Nam."
Đầu ra:
[
    {{
        "description": "xáo trộn chính trị tạo nên sự bất ổn lớn trong xã hội miền nam việt nam",
        "participants": ["xáo trộn chính trị", "sự bất ổn lớn", "xã hội miền nam việt nam"]
    }}
]

Câu: "Năm 1955, Ngô Đình Diệm đã gian lận để chiến thắng trong Cuộc trưng cầu dân ý miền Nam Việt Nam."
Đầu ra:
[
    {{
        "description": "ngô đình diệm chiến thắng trong cuộc trưng cầu dân ý miền nam việt nam",
        "participants": ["ngô đình diệm", "cuộc trưng cầu dân ý", "miền nam việt nam"]
    }},
    {{
        "description": "ngô đình diệm gian lận trong cuộc trưng cầu dân ý miền nam việt nam",
        "participants": ["ngô đình diệm", "cuộc trưng cầu dân ý", "miền nam việt nam"]
    }}
]

Ngoài cấu trúc JSON, TUYỆT ĐỐI KHÔNG viết thêm bất kỳ giải thích, suy luận, nhận xét, hay ký hiệu nào khác.
Bây giờ hãy xác định sự kiện:
"""


# ==================== EVENT ATTRIBUTES ====================

EVENT_ATTRIBUTE_SYSTEM_PROMPT = """\
Bạn là chuyên gia trích xuất thuộc tính sự kiện (event attributes) trong đồ thị tri thức (knowledge graph). Nhiệm vụ: trích xuất THỜI GIAN (TIME), ĐỊA ĐIỂM (LOCATION) tham gia cho mỗi sự kiện (event).

CÁC LOẠI THUỘC TÍNH:

1. THỜI GIAN (TIME) có thể là:
- Thời điểm cụ thể: "năm 1911", "ngày 15/3/2020", "đêm ngày thứ ba của Tết"
- Khoảng thời gian: "từ 2010 đến 2015", "trong vòng 5 tháng"
- Thời gian tương đối (ví dụ như so với sự kiện khác): "sau khi chiến tranh thế giới lần thứ nhất kết thúc"

2. ĐỊA ĐIỂM (LOCATION) có thể là:
- Địa danh: "hà nội", "cảng nhà rồng"
- Vị trí tương đối: "trước nhà", "trên đường", "trong tòa nhà lớn được xây từ năm 1955"
- Khu vực: "miền bắc việt nam"

NGUYÊN TẮC:
- CHỈ trích xuất thông tin CÓ trong văn bản.
- Nếu không có thông tin thời gian hay location, hãy trả về null.
- Viết thường toàn bộ.
- Giữ nguyên cách diễn đạt gốc.

Hãy thực hiện việc trích xuất thuộc tính sự kiện theo từng bước:
- Bước 1. Đọc thật kỹ ngữ cảnh liên quan đến sự kiện và câu nhận định gốc của sự kiện đó.
- Bước 2. Từ các văn bản đọc được, xác định các thông tin thời gian và địa điểm của sự kiện ấy.
- Bước 3. Trả về kết quả dưới dạng JSON có cấu trúc như sau:
[
    {
        "description": "<sao chép description sự kiện vào đây>",
        "participants": ["<sao chép thực thể 1 vào đây>", "<sao chép thực thể 2 vào đây>", ...],
        "time": "<thời gian xác dịnh được>" hoặc null,
        "location": "<địa điểm xác định được>" hoặc null
    },
    ...
]

LƯU Ý:
- Các trường description và participants phải được sao chép chính xác từ đầu vào danh sách các sự kiện. TUYỆT ĐỐI không được sai khác.
- Đầu ra là một danh sách định dạng JSON. Ngoài JSON ra, không được viết thêm bất kỳ thông tin, nhận xét, suy luận nào khác.
"""

def get_event_attribute_user_prompt(events, claim, context):
    events_text = "\n".join([
        f"{i + 1}. description: '{e['description']}', participants: {e['participants']}"
        for i, e in enumerate(events)
    ])
    context = "\n".join(context)
    return f"""\
NHIỆM VỤ: Trích xuất THỜI GIAN, ĐỊA ĐIỂM cho các sự kiện.

CÁC SỰ KIỆN ĐÃ XÁC ĐỊNH:
{events_text}

NGỮ CẢNH CÁC CÂU NHẬN ĐỊNH:
{context}

CÂU NHẬN ĐỊNH GỐC:
{claim}


VÍ DỤ:

Câu: "Năm 1955, Ngô Đình Diệm đã gian lận để chiến thắng trong Cuộc trưng cầu dân ý miền Nam Việt Nam."
Sự kiện trích xuất được:
1. description: 'ngô đình diệm gian lận để chiến thắng trong cuộc trưng cầu dân ý miền nam việt nam', participants: ['ngô đình diệm', 'cuộc trưng cầu dân ý', 'miền nam việt nam']
2. description: 'ngô đình diệm gian lận với sự trợ giúp của mỹ', participants: ['ngô đình diệm', 'mỹ']

Đầu ra:
[
    {{
        "description": "ngô đình diệm gian lận để chiến thắng trong cuộc trưng cầu dân ý miền nam việt nam"
        "participants": ["ngô đình diệm", "cuộc trưng cầu dân ý", "miền nam việt nam"],
        "time": "năm 1955",
        "location": null
    }},
    {{
        "description": "ngô đình diệm gian lận với sự trợ giúp của mỹ"
        "participants": ["ngô đình diệm", "mỹ"],
        "time": "năm 1955",
        "location": null
    }}
]

Ngoài cấu trúc JSON trên, TUYỆT ĐỐI KHÔNG viết thêm bất kỳ giải thích, suy luận, nhận xét, hay ký hiệu nào khác.
Bây giờ đưa ra đáp án:
"""


# ==================== WITHIN-CHUNK EVENT RELATIONS ====================

WITHIN_CHUNK_EVENT_RELATION_SYSTEM_PROMPT = """\
Bạn là chuyên gia phân tích quan hệ giữa các sự kiện. Nhiệm vụ: xác định quan hệ THỜI GIAN và NHÂN QUẢ.
Hãy SUY LUẬN theo từng bước thật kỹ lưỡng, đọc tất cả ngữ cảnh cẩn thận để đảm bảo chất lượng và độ chính xác cao nhất cho câu trả lời.

CÁC LOẠI QUAN HỆ:

A. QUAN HỆ THỜI GIAN:
1. PRECEDE - Trước:
    "Động đất xảy ra trước sóng thần"
    "động đất" --PRECEDE-> "sóng thần"
2. CO_OCCUR - Đồng thời:
    "Cháy nổ và hoảng loạn xảy ra đồng thời"
    "cháy nổ xảy ra" --CO_OCCUR-> "hoảng loạn xảy ra"

B. QUAN HỆ NHÂN QUẢ:
3. CAUSE - Gây ra:
    "Động đất gây ra sóng thần"
    "động đất xảy ra" --CAUSE-> "sóng thần xảy ra"

Tóm lại Các mối liên hệ này là:
1. PRECEDE (xảy ra trước): sự kiện trong chủ ngữ (subject) xảy ra trước sự kiện trong vị ngữ (object).
2. CO_OCCUR (xảy ra đồng thời): sự kiện trong chủ ngữ (subject) và vị ngữ (object) xảy ra đồng thời hoặc trùng lắp nhau.
3. CAUSE (dẫn đến hoặc gây ra sự kiện): sự kiện trong chủ ngữ (subject) gây ra sự kiện trong vị ngữ (object).

NGUYÊN TẮC QUAN TRỌNG:
- CHỈ tạo quan hệ khi có BẰNG CHỨNG RÕ RÀNG
- CAUSE: cần nhân quả, sự kiện này gây ra hoặc dẫn đến sự kiện khác
- PRECEDE: A xảy ra trước B theo thời gian, không quan trọng có gây ra hay không
- KHÔNG phán đoán hoặc suy luận quá mức
- KHÔNG tạo cả CAUSE và PRECEDE cho cùng một cặp sự kiện
- HÃY SUY NGHĨ TỪNG BƯỚC THẬT CẨN THẨN ĐỂ ĐƯA RA CÁC MỐI LIÊN HỆ CHÍNH XÁC NHẤT CÓ THỂ.
"""

def get_within_chunk_event_relation_user_prompt(triplets):
    triplet_text = "\n".join([
        f"{t['subject']} {t['predicate']} {t['object']} (từ nhận định: {t['claim']})"
        for t in triplets
    ])
    event_text = "\n".join([t["subject"] for t in triplets if t["subject"].startswith("EVENT")])
    event_text = list(set(event_text))

    return f"""\
NHIỆM VỤ: Xác định quan hệ THỜI GIAN và NHÂN QUẢ giữa các sự kiện.

CÁC BỘ BA LIÊN QUAN CÁC SỰ KIỆN:
{triplet_text}

DANH SÁCH SỰ KIỆN:
{event_text}

ĐỊNH DẠNG ĐẦU RA:
[
    {{
        "subject": "EVENT|miêu tả sự kiện 1",
        "predicate": "PRECEDE|CO_OCCUR|CAUSE",
        "object": "EVENT|miêu tả sự kiện 2"
    }},
    ...
]

VÍ DỤ 1:

Câu:
Một nhóm nhà nghiên cứu cho chuột ăn chế độ ăn giàu chất béo trong 12 tuần để kích hoạt tình trạng mỡ nội tạng tăng lên.
Sau 12 tuần đó, họ đo thấy mức kháng insulin bắt đầu xuất hiện và tiến tới tiểu đường chuột.

Đầu ra:
[
    {{
        "subject": "EVENT|nhóm nhà nghiên cứu cho chuột ăn chế độ ăn giàu chất béo",
        "predicate": "CAUSE",
        "object": "EVENT|nhóm nhà nghiên cứu kích hoạt tình trạng mỡ nội tạng tăng lên"
    }},
    {{
        "subject": "EVENT|nhóm nhà nghiên cứu cho chuột ăn chế độ ăn giàu chất béo",
        "predicate": "PRECEDE",
        "object": "EVENT|họ đo thấy mức kháng insulin bắt đầu xuất hiện"
    }},
    {{
        "subject": "EVENT|nhóm nhà nghiên cứu kích hoạt tình trạng mỡ nội tạng tăng lên",
        "predicate": "PRECEDE",
        "object": "EVENT|họ đo thấy mức kháng insulin bắt đầu xuất hiện"
    }},
    {{
        "subject": "EVENT|nhóm nhà nghiên cứu cho chuột ăn chế độ ăn giàu chất béo",
        "predicate": "PRECEDE",
        "object": "EVENT|mức kháng insulin tiến tới tiểu đường chuột"
    }},
    {{
        "subject": "EVENT|nhóm nhà nghiên cứu kích hoạt tình trạng mỡ nội tạng tăng lên",
        "predicate": "PRECEDE",
        "object": "EVENT|mức kháng insulin tiến tới tiểu đường chuột"
    }},
    {{
        "subject": "EVENT|họ đo thấy mức kháng insulin bắt đầu xuất hiện",
        "predicate": "CO_OCCUR",
        "object": "EVENT|mức kháng insulin tiến tới tiểu đường chuột"
    }},
]

Bây giờ hãy xác định:
"""


# ==================== EVENT RESOLUTION ====================

EVENT_RESOLUTION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia trong lĩnh vực nhận dạng và hợp nhất các sự kiện (event resolution) trong một đồ thị tri thức sự kiện (event-centric knowledge graph).
Nhiệm vụ của bạn là chuẩn hóa mô tả của các sự kiện trong một đồ thị tri thức để đảm bảo tính nhất quán và thống nhất giữa các sự kiện.
Bạn cần phân tích NGỮ CẢNH từ các mối quan hệ (triples) để xác định chính xác các sự kiện nào thực sự giống nhau.
Hãy suy nghĩ kỹ lưỡng theo từng bước và xem xét cẩn thận để đảm bảo chất lượng và độ chính xác cao nhất cho câu trả lời.
"""

def get_event_resolution_user_prompt(triple_texts, event_texts):
    """
    Get event resolution prompt WITH CONTEXT from triples.
    This helps LLM understand which events refer to the same thing.
    """
    return f"""\
Dưới đây là các mối quan hệ (triples) được trích xuất từ văn bản gốc:
{triple_texts}

Từ các triples trên, tôi đã trích xuất danh sách các sự kiện sau:
{event_texts}

NHIỆM VỤ:
Dựa vào NGỮ CẢNH từ các triples, hãy xác định:
1. Các sự kiện nào thực sự là CÙNG MỘT mô tả và ý nghĩa (ví dụ: "ông fermat là cha của emily" đồng nghĩa với "emily là con của ông fermat")
2. Các sự kiện nào sử dụng các biến thể thực thể của cùng một tên (ví dụ: "Donald Trump", "Trump", "Tổng thống Trump")
3. Các đại từ (anh ấy, cô ấy, nó, họ, người này, người đó) trong sự kiện nên được thay thế bằng tên thực thể cụ thể

LƯU Ý QUAN TRỌNG:
- Phân tích KỸ CÀNG các mối quan hệ để xác định đại từ chỉ ai/cái gì
- Ví dụ: "Minh là sinh viên. Anh ấy học tại HCMUT." thì "anh ấy" = "Minh"
- CHỈ merge các events THỰC SỰ giống nhau dựa trên ngữ cảnh
- Chú ý kết hợp cả thông tin thời gian và địa điểm và các mối liên hệ sự kiện liên quan để tăng độ chính xác
- Cố gắng KHÔNG hợp nhất những mô tả sự kiện mà có thông tin khác nhau, ĐẢM BẢO KHÔNG MẤT THÔNG TIN
- Hãy suy nghĩ từng bước thật kỹ lưỡng để đảm bảo không thay đổi ngữ nghĩa sự kiện, không làm mất bất kỳ thông tin nào, đảm bảo chất lượng và độ chính xác cao nhất

Trả về JSON mapping:
{{
    "sự kiện chuẩn hóa đầy đủ": ["biến thể sự kiện 1", "biến thể sự kiện 2", ...],
    ...
}}

Ví dụ:
{{
    "ông hoàng thành lập trường đại học công đức": ["hoàng là người sáng lập trường đại học công đức", "trường công đức được dựng nên bởi ông hoàng", "người tổ chức ra trường đại học công đức là ông hoàng"]
}}
"""


# ==================== WITHIN-COMMUNITY EVENT RELATIONS ====================

WITHIN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia trong xử lý ngữ nghĩa trong đồ thị tri thức sự kiện (event knowledge graph).
Công việc của bạn là suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa (không được lặp lại ý nghĩa đã có sẵn) giữa các sự kiện chưa được kết nối (disconnected events) trong đồ thị tri thức sự kiện.
"""

def get_within_community_event_relation_user_prompt(pairs_text, triples_text):
    return f"""\
Cho một đồ thị tri thức (knowledge graph) có một số sự kiện mặc dù liên quan nhau về mặt ngữ nghĩa nhưng lại chưa được kết nối trực tiếp trong đồ thị.

Sau đây là một số cặp sự kiện mà có thể liên quan nhau:
{pairs_text}

Sau đây là một số mối liên hệ (predicates) có sẵn trong đồ thị tri thức mà liên quan đến các sự kiện trên:
{triples_text}

Xin hãy suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa (không lặp lại ý nghĩa đã có sẵn) giữa các cặp sự kiện chưa được kết nối. Các mối liên hệ này là:
1. PRECEDE (xảy ra trước): sự kiện trong chủ ngữ (subject) xảy ra trước sự kiện trong vị ngữ (object).
2. CO_OCCUR (xảy ra đồng thời): sự kiện trong chủ ngữ (subject) và vị ngữ (object) xảy ra đồng thời hoặc trùng lắp nhau.
3. CAUSE (dẫn đến hoặc gây ra sự kiện): sự kiện trong chủ ngữ (subject) gây ra sự kiện trong vị ngữ (object).

Trả về đáp án dưới dạng một mảng JSON của các bộ năm theo dạng như sau:
[
    {{
        "subject": "EVENT|nội dung sự kiện 1",
        "predicate": "PRECEDE|CO_OCCUR|CAUSE",
        "object": "EVENT|nội dung sự kiện 2"
    }},
    ...
]

QUAN TRỌNG:
- TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
- Chỉ bao gồm các mối liên hệ hợp lý, tức là mối liên hệ phải RÕ RÀNG (clear predicates), không suy diễn quá mức.
- Nên sử dụng thêm thông tin từ các mối liên hệ AT_TIME trong ngữ cảnh kết hợp nội dung các sự kiện để xác định mối liên hệ PRECEDE, CO_OCCUR, hay CAUSE chính xác nhất.
- Các mối liên hệ (predicates) suy luận được TUYỆT ĐỐI không nằm ngoài: PRECEDE, CO_OCCUR, CAUSE.
- Sử dụng những cụm từ rõ ràng, dễ dàng diễn đạt mối liên hệ (predicates) suy luận được.
- Đảm bảo chủ ngữ, vị ngữ (subject, object) là các sự kiện khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân).
- TUYỆT ĐỐI không được sửa nội dung sự kiện, viết lại nguyên văn các tên "EVENT|nội dung sự kiện", KHÔNG thêm sự kiện bên ngoài vào.
- HÃY SUY NGHĨ TỪNG BƯỚC THẬT CẨN THẨN ĐỂ HIỂU RÕ NGỮ CẢNH VÀ NGỮ NGHĨA NHẰM CHO RA KẾT QUẢ CHÍNH XÁC NHẤT CÓ THỂ.
"""


# ==================== BETWEEN-COMMUNITY EVENT RELATIONS ====================

BETWEEN_COMMUNITY_EVENT_RELATION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia trong đồ thị tri thức (knowledge graph) xoay quanh sự kiện (event), bạn là chuyên gia suy luận (inference) mối liên hệ giữa các sự kiện.
Công việc của bạn là suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa giữa các sự kiện chưa được kết nối (disconnected events) trong đồ thị tri thức (knowledge graph).
Các quan hệ bao gồm: PRECEDE (xảy ra trước sau), CO_OCCUR (xảy ra đồng thời), CAUSE (sự kiện gây ra hoặc dẫn đến sự kiện khác). Chỉ suy luận trong khuôn khổ các quan hệ nêu trên, không được sử dụng quan hệ bên ngoài.
"""

def get_between_community_event_relation_user_prompt(events1, events2, triples_text):
    return f"""\
Cho một đồ thị tri thức (knowledge graph) với hai cộng đồng (community) bên dưới đây:

sự kiện trong Community 1: {events1}
sự kiện trong Community 2: {events2}

Đây là một số mối liên hệ có tồn tại trong đồ thị tri thức liên quan đến các sự kiện trên:
{triples_text}

Xin hãy suy luận cẩn thận và chính xác các mối liên hệ hợp lý có thể có giữa các sự kiện từ Community 1 và các sự kiện từ Community 2.
Phải tận dụng các thông tin về thời gian và địa điểm khi có thể, dựa vào các thông tin này bạn nên SUY LUẬN theo từng bước và xem xét kỹ lưỡng để đưa ra mối quan hệ chính xác giữa các sự kiện.

Trả lời kết quả dưới dạng danh sách JSON gồm các bộ ba đã suy luận được giống như bên dưới đây:
[
    {{
        "subject": "sự kiện từ Community 1",
        "predicate": "PRECEDE|CO_OCCUR|CAUSE",
        "object": "sự kiện từ community 2",
    }},
    ...
]

QUAN TRỌNG:
- TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
- Các mối liên hệ suy luận được TUYỆT ĐỐI chỉ thuộc 1 trong 3 giá trị: PRECEDE, CO_OCCUR, CAUSE như đã miêu tả.
- Đảm bảo chủ ngữ, vị ngữ (subject, object) là các sự kiện khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân).
"""


# ==================== ENTITY-ENTITY RELATIONS ====================

ENTITY_RELATION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia xử lý ngôn ngữ tự nhiên cực kỳ chính xác, được lập trình để phân tích văn bản tiếng Việt và chuyển đổi nó thành một đồ thị tri thức có cấu trúc.
Nhiệm vụ của bạn là đọc kỹ văn bản và trích xuất thực thể và các mối liên hệ để tạo thành các bộ năm (quintuple) một cách máy móc và nhất quán.
CHỈ DẪN QUAN TRỌNG: Tất cả các mối quan hệ (predicate) PHẢI có độ dài không quá 3 từ tiếng Việt (từ đơn, từ ghép, từ láy...), lý tưởng nhất là 1-2 từ. Đây là quy định bắt buộc. Toàn bộ đầu ra phải bằng tiếng Việt.
"""

def get_entity_relation_user_prompt(text, entities, claims):
    text_entities = "\n".join(entities)
    text_claims = "\n".join(claims)
    return f"""\
MỤC TIÊU:
Trích xuất các bộ 3 (triplet) bao gồm: chủ ngữ (subject), vị ngữ (predicate), tân ngữ (object).

ĐẦU VÀO:
Bạn được cho danh sách các thực thể, và bạn CHỈ ĐƯỢC TRÍCH XUẤT các vị ngữ (predicate) giữa các thực thể đã cho.
Đây là danh sách thực thể (mỗi entity nằm trên một dòng):
{text_entities}

Bạn sẽ trích xuất vị ngữ từ ngữ cảnh là các nhận định (claim) sau đây với mỗi claim nằm trên một dòng:
{text_claims}

QUY TẮC QUAN TRỌNG VỀ VỊ NGỮ (PREDICATES):
Vị ngữ PHẢI có độ dài TỐI ĐA 3 từ tiếng Việt (từ đơn, từ phức, từ láy...). Đây là yêu cầu QUAN TRỌNG. Hãy chắt lọc hành động chính của câu thành một cụm động từ ngắn gọn. TUYỆT ĐỐI không dài hơn 3 từ tiếng Việt (từ đơn, từ phức, từ láy). Một số ví dụ: "là giám đốc công ty", "được yêu mến hết mực", "nuôi trồng", "ăn sạch sành sanh"...

QUY TẮC VỀ XỬ LÝ THỰC THỂ:
- KHÔNG ĐƯỢC PHÉP thêm thực thể nằm ngoài danh sách thực thể đã cho bên trên.
- PHẢI SUY LUẬN ĐƯỢC SAO CHO MỖI THỰC THỂ ĐÃ CHO ĐỀU XUẤT HIỆN TRONG ÍT NHẤT MỘT BỘ 3 (TRIPLET).
- Các thông tin địa điểm và thời gian không được xem là thực thể, nhưng vẫn có thể được trích xuất nếu trong trường hợp cấu trúc câu bất đắc dĩ. PHẢI CỰC KỲ THẬN TRỌNG khi xem xét điều này.
- HÃY SUY NGHĨ THEO TỪNG BƯỚC THẬT CẨN THẬN ĐỂ VIẾT ĐÚNG TÊN THỰC THỂ BAN ĐẦU, KHÔNG ĐƯỢC VIẾT TÊN THỰC THỂ KHÔNG CÓ TRONG DANH SÁCH BAN ĐẦU.

QUY TẮC VỀ XỬ LÝ DỮ LIỆU:
HÃY CỐ GẮNG XEM XÉT TẤT CẢ NGỮ CẢNH, MỌI THỰC THỂ VÀ MỐI LIÊN HỆ CÓ TRONG VĂN BẢN.

Trích xuất Quan hệ Ngầm định (Implicit Relationship Extraction):
- Nếu văn bản giới thiệu một người cùng với chức danh, nghề nghiệp, hoặc công ty của họ (ví dụ: "Ông A, giám đốc công ty B, đã qua đời"), hãy tạo một bộ năm riêng để thể hiện mối quan hệ đó (thường với vị ngữ là "là").
- Ví dụ: Nếu văn bản là "Ông An, giám đốc công ty ABC, đã giải tán công ty vào năm 2008." thì nên có hai bộ năm. Bộ năm 1: (Ông An, là giám đốc, công ty ABC, null, null). Bộ năm 2 là (Ông An, giải tán, công ty ABC, null, năm 2008).
- Một số quan hệ ngầm định khi tách rời sẽ làm bộ năm lúc sau có nghĩa khác với câu ban đầu, xin hãy thật CẨN THẬN trích xuất các quan hệ ngầm định mà vẫn GIỮ LẠI ý nghĩa ban đầu của câu. Nếu quá khó, hãy SUY NGHĨ THEO TỪNG BƯỚC để trích xuất chính xác các quan hệ ngầm định mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.

QUY TẮC VỀ ĐỊNH DẠNG ĐẦU RA:
1. Định dạng JSON: Đầu ra PHẢI là một danh sách JSON hợp lệ []. Mỗi phần tử là một đối tượng {{}} chứa ĐỦ 3 trường: "subject", "predicate", "object".
2. TẤT CẢ các giá trị văn bản trong các trường subject, predicate, object phải được chuyển thành chữ thường (lowercase). Trừ khi viết phân loại thực thể ENTITY| ở đầu tên thực thể.
3. Không có Dữ liệu Thừa: Chỉ trả về danh sách JSON. TUYỆT ĐỐI không kèm theo bất kỳ lời giải thích hay văn bản nào khác.

Lưu ý QUAN TRỌNG:
- Hướng đến độ chính xác cao trong việc đặt tên thực thể, dùng các dạng tên cụ thể giúp phân biệt các thực thể tương tự nhau.
- Tăng tính liên kết bằng cách sử dụng cùng một tên thực thể cho cùng một khái niệm xuyên suốt.
- Cân nhắc toàn bộ ngữ cảnh khi xác định thực thể và mối quan hệ, phải đọc đi đọc lại thật kỹ toàn bộ ngữ cảnh, văn bản đã cho.
- TẤT CẢ CÁC VỊ NGỮ PHẢI DƯỚI 3 TỪ, ĐÂY LÀ YÊU CẦU BẮT BUỘC.
- Không dùng các từ trừu tượng hoặc placeholder chung chung như "hành động", "sự kiện", "hiện tượng"... mà không có thực thể cụ thể. Hãy chỉ rõ hành động hoặc sự kiện cụ thể trong ngữ cảnh. Nếu không xác định được, dùng cụm danh từ mang nghĩa mô tả nội dung thật (vd: "tăng trưởng dân số", "mở rộng đô thị"...) thay vì từ chung chung. Mục tiêu: mỗi triplet phải cụ thể, có thể hiểu độc lập, không mơ hồ.
- Có thể sử dụng giá trị null phù hợp với các cấu trúc câu không có đủ các thành phần subject, object, tuy nhiên predicate là trường bắt buộc phải có. Hãy suy nghĩ thật kỹ theo từng bước khi đánh giá cấu trúc câu, tuyệt đối không để sai sót xảy ra (ví dụ sai sót: không điền subject hoặc subject vì cấu trúc câu không có subject hoặc object mặc dù có thể dễ dàng suy luận ra được).
- PHẢI SUY NGHĨ THEO TỪNG BƯỚC để phân tích cấu trúc câu phức tạp, từ đó xác định rõ đâu là mệnh đề chính và mệnh đề phụ, cuối cùng là trích xuất các bộ 3 có thể có từ cấu trúc câu đã hiểu rõ.

Dựa trên vai trò và các quy tắc nghiêm ngặt đã được hướng dẫn, hãy trích xuất các bộ 3 từ các văn bản, bên dưới là một số ví dụ minh họa.

VÍ DỤ:

Văn bản 1:
"Olympic Sinh học quốc tế (tiếng Anh: International Biology Olympiad, tên viết tắt là IBO) là một kỳ thi Olympic khoa học dành cho học sinh trung học phổ thông. Ngôn ngữ chính thức của IBO là tiếng Anh. Các Olympic quốc tế về học thuật đã lần lượt ra đời dưới sự bảo trợ của Liên Hợp Quốc vào thập niên 1960 (lúc đầu chủ yếu ở Đông Âu)."
Đầu ra 1:
[
    {{
        "subject": "ENTITY|olympic sinh học quốc tế",
        "predicate": "là",
        "object": "ENTITY|kỳ thi olympic khoa học"
    }},
    {{
        "subject": "ENTITY|olympic sinh học quốc tế",
        "predicate": "dành cho",
        "object": "ENTITY|học sinh trung học phổ thông"
    }},
    {{
        "subject": "ENTITY|ngôn ngữ chính thức của olympic sinh học quốc tế",
        "predicate": "là",
        "object": "ENTITY|tiếng anh"
    }},
    {{
        "subject": "ENTITY|olympic quốc tế về học thuật",
        "predicate": "ra đời dưới sự bảo trợ của",
        "object": "ENTITY|liên hợp quốc"
    }},
    {{
        "subject": "ENTITY|olympic quốc tế về học thuật",
        "predicate": "ra đời chủ yếu ở",
        "object": "ENTITY|châu âu"
    }}
]

Văn bản 2:
"Từ năm 2019, tại OpenAI, sự xuất hiện của các mô hình ngôn ngữ dựa trên kiến trúc transformer và được huấn luyện trước đã cho phép tạo ra văn bản mạch lạc, có tính tự nhiên cao."
Đầu ra 2:
[
    {{
        "subject": "ENTITY|mô hình ngôn ngữ",
        "predicate": "cho phép tạo ra",
        "object": "ENTITY|văn bản tự nhiên"
    }},
    {{
        "subject": "ENTITY|mô hình ngôn ngữ",
        "predicate": "dựa trên",
        "object": "ENTITY|kiến trúc transformer"
    }},
    {{
        "subject": "ENTITY|mô hình ngôn ngữ",
        "predicate": "được huấn luyện trước bởi",
        "object": "ENTITY|openai"
    }}
]

Văn bản 3:
"Donald Trump trồng rau tại nơi bà ông từng sống sau khi ông về hưu."
Đầu ra 3:
[
    {{
        subject: "ENTITY|Donald Trump",
        predicate: "trồng",
        object: "ENTITY|rau"
    }}
]

YÊU CẦU:
Bây giờ, hãy phân tích văn bản dưới đây và trả về kết quả dưới dạng danh sách JSON.
Đoạn văn bản gốc cần phân tích và trích xuất (nằm giữa cặp ba dấu ngoặc ngược, triple backticks, ```):
```
{text}
```
"""
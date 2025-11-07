"""Centralized repository for all LLM prompts used in the knowledge graph system."""

# Pre-KG entity resolution
PREKG_ENTITY_RESOLUTION_SYSTEM_PROMPT = """\
Bạn là một trợ lý ngôn ngữ thông minh, chuyên gia trong lĩnh vực phân tích ngôn ngữ. Bạn có khả năng phân tích, hiểu rõ các biến thể (biểu diễn, câu chữ khác nhau) của cùng một thực thể. Bạn cũng hiểu rõ cách cú pháp tiếng Việt lược bỏ một số thực thể trong câu và có thể phục hồi lại thông tin bị lược bỏ dễ dàng.
Quá trình tìm ra các biến thể của cùng một thực thể, và thay thế các biến thể thành một cụm từ duy nhất được gọi là chuẩn hóa thực thể.
"""

def get_prekg_entity_resolution_user_prompt(text):
    prompt = f"""\
**Nhiệm vụ của bạn:**
Nhận một văn bản đầu vào và trả về văn bản mới **đã chuẩn hóa tất cả các thực thể** theo yêu cầu trên.

Các yêu cầu QUAN TRỌNG:
- Mọi từ hoặc cụm từ **chỉ cùng một thực thể** (bao gồm tên đầy đủ, biệt danh, đại từ, các cách viết tắt, alias, nickname, v.v.) phải được thay thế bằng **một tên chuẩn hóa duy nhất**.  
- Tên chuẩn hóa nên là **tên đầy đủ, rõ ràng và dễ nhận biết**.  
- Giữ nguyên ngữ cảnh và các từ khác trong văn bản, chỉ thay thế từ/biến thể của thực thể đó.
- Không thay đổi các thực thể khác, chỉ nhóm các biến thể của cùng một thực thể.
- Cố gắng xem xét tất cả tên biến thể có trong văn bản, ngay cả tên mã như biển số xe, mã số sinh viên... Cố gắng làm cho các thực thể có tên cụ thể nhất có thể, tránh các danh từ chung chung như "biển số xe" (không biết số nào), "cảnh sát giao thông" (không biết cảnh sát vùng nào).
- Một số câu có chủ ngữ hoặc tân ngữ bị lược bỏ (do cú pháp tiếng Việt), hãy phục hồi chủ ngữ hoặc tân ngữ đó bằng tên chuẩn hóa phù hợp nhất.
- Đầu ra chỉ viết lại văn bản đã chuẩn hóa, không viết các chi tiết bên ngoài như luồng suy nghĩ, đánh giá thêm...

**Ví dụ:**

Ví dụ 1
Văn bản gốc:
"
Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa. Trong đó, hiến chương này cũng nói rằng đất nước này không được thực hiện chính sách thực dân.
Hiến chương Pháp ngữ 1977 quy định Pháp là nước gì?
Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa.
"

Văn bản sau chuẩn hóa:
"
Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa. Trong đó, Hiến chương Pháp ngữ 1977 này cũng nói rằng nước Pháp không được thực hiện chính sách thực dân.
Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước gì?
Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa.
"

Ví dụ 2
Văn bản gốc:
"
Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011. Chiếc ô tô đã được quân đội truy lùng và dừng lại ngay trên con đường đó. Hiện con đường đang bị niêm phong chờ việc điều tra.
Tai nạn do ô tô gây ra trên con đường đó có phải là cố tình?
Mặc dù không có bằng chứng cho thấy sự cố ý, song vụ tai nạn chủ yếu gây chết người đối với các quan chức cấp cao trong Nhà nước, vấy lên lo ngại đây là một vụ ám sát.
"

Văn bản sau chuẩn hóa:
"
Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011. Ô tô ABA-170 đã được quân đội truy lùng và dừng lại ngay trên con đường Tô Hiến Thành. Hiện con đường Tô Hiến Thành đang bị niêm phong chờ việc điều tra.
Tai nạn do ô tô ABA-170 gây ra trên con đường Tô Hiến Thành có phải là cố tình?
Mặc dù không có bằng chứng cho thấy sự cố ý, song vụ tai nạn do ô tô ABA-170 trên đường Tô Hiến Thành chủ yếu gây chết người đối với các quan chức cấp cao trong Nhà nước, vấy lên lo ngại đây là một vụ ám sát.
"

Ví dụ 3
Văn bản gốc:
"
Đến thời kỳ đồ sắt, vào khoảng thế kỷ 8 TCN đã xuất hiện nhà nước đầu tiên của người Việt được khảo cổ học xác nhận trên miền Bắc Việt Nam ngày nay. Theo sử sách, đó là Nhà nước Văn Lang của các vua Hùng.
Như vậy, có phải nhà nước đầu tiên của người Việt hình thành từ thời kỳ đồ đá?
Không, ra đời thời kỳ đồ sắt mới đúng.
"

Văn bản sau chuẩn hóa:
"
Đến thời kỳ đồ sắt, vào khoảng thế kỷ 8 TCN đã xuất hiện nhà nước Văn Lang của người Việt được khảo cổ học xác nhận trên miền Bắc Việt Nam ngày nay. Theo sử sách, đó là Nhà nước Văn Lang của các vua Hùng.
Như vậy, có phải nhà nước Văn Lang của người Việt hình thành từ thời kỳ đồ đá?
Không, nhà nước Văn Lang ra đời thời kỳ đồ sắt mới đúng.
"

Văn bản cần phân tích (nằm giữa ba dấu ```):
```
{text}
```
"""
    return prompt


CLAIM_EXTRACTION_SYSTEM_PROMPT = """\
Bạn là một cỗ máy xử lý ngôn ngữ tự nhiên cực kỳ chính xác, được lập trình để phân tách một văn bản dài thành các tuyên bố (claim).
Các tuyên bố (claim) là các mệnh đề khẳng định (declarative statements) mà có thể kiểm chứng tính đúng sai, khác với các câu nói như câu hỏi, câu cảm thán...
"""

def get_claim_extraction_user_prompt(text):
    return f"""\
Bạn là một trợ lý ngôn ngữ thông minh.
Nhiệm vụ của bạn là trích xuất tất cả các câu khẳng định (declarative statements) từ đoạn văn bản dưới đây (được bao quanh bởi ba dấu ```).

Lưu ý QUAN TRỌNG:
- Câu khẳng định là những câu thể hiện một ý kiến, sự kiện hoặc thông tin có thể được xác minh là đúng hoặc sai, không phải câu hỏi, câu cảm thán...
- Nếu có thông tin liên quan địa điểm, thời gian gắn với câu khẳng định (claim), hãy cố gắng viết câu đó (claim) thành một câu có cả thông tin địa điểm, thời gian.
- Đầu ra chỉ viết các câu khẳng định (claim) đã trích xuất được, không thêm các chi tiết bên ngoài như luồng suy nghĩ, đánh giá, nhận xét...
- Khi xuất hiện các thông tin viết tắt hoặc ngầm định trong câu thì phải hiểu nghĩa ngầm định và tách thành một nhận định riêng. Ví dụ như "ông Đại Ngô (1969 đến 2020), giám đốc công ty X, đã quyên góp 10 tỷ đô cho trẻ em nghèo" phải được tách thành "ông Đại Ngô sinh năm 1969", "ông Đại Ngô chết năm 2020", "ông Đại Ngô là giám đốc công ty X", "ông Đại Ngô đã quyên góp 10 tỷ đô cho trẻ em nghèo".

Các bước thực hiện:
- Bước 1: Đọc kỹ đoạn văn bản và chuẩn hóa tất cả các thực thể trong văn bản để đảm bảo tính nhất quán.
- Bước 2: Xác định và trích xuất tất cả các câu khẳng định từ đoạn văn bản đã chuẩn hóa.
- Bước 3: Trả về kết quả dưới dạng một các câu khẳng định, mỗi câu trên một dòng.

Ví dụ 1:
```
Fred Trump là cha Donald Trump. Donald Trump từng học tại Đại học Wharton. Những người từng học ở đây đều không tham gia chính trị. Nhưng Trump là một ngoại lệ trong số họ.
```

Fred Trump là cha của Donald Trump.
Donald Trump từng học tại Đại học Wharton.
Người học ở Đại học Wharton không tham gia chính trị.
Donald Trump là một ngoại lệ.

Ví dụ 2:
```
Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011. Chiếc ô tô đã được quân đội truy lùng và dừng lại ngay trên con đường đó. Hiện con đường đang bị niêm phong chờ việc điều tra.
Tai nạn do ô tô ABA-170 gây ra trên con đường Tô Hiến Thành có phải là cố tình?
Mặc dù không có bằng chứng cho thấy sự cố ý, song vụ tai nạn do ô tô ABA-170 trên đường Tô Hiến Thành chủ yếu gây chết người đối với các quan chức cấp cao trong Nhà nước, vấy lên lo ngại đây là một vụ ám sát.
```

Ô tô ABA-170 chạy trên đường Tô Hiến Thành đã tông chết nhiều người trong vụ tai nạn đêm ngày 16 tháng 05 năm 2011.
Ô tô ABA-170 đã được quân đội truy lùng.
Ô tô ABA-170 đã được quân đội dừng lại.
Con đường Tô Hiến Thành đang bị niêm phong.
Con đường Tô Hiến Thành đang chờ việc điều tra.
Vụ tai nạn do ô tô ABA-170 trên đường Tô Hiến Thành không có bằng chứng cho thấy sự cố ý.
Vụ tai nạn do ô tô ABA-170 trên đường Tô Hiến Thành chủ yếu gây chết người đối với các quan chức cấp cao trong Nhà nước.
Vụ tai nạn do ô tô ABA-170 trên đường Tô Hiến Thành bị lo ngại là một vụ ám sát.

Văn bản cần phân tích (nằm giữa ba dấu ```):
```
{text}
```
"""

# Phase 2: Entity standardization prompts

ENTITY_RESOLUTION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia trong lĩnh vực nhận dạng và hợp nhất thực thể (entity resolution) cũng như biểu diễn tri thức (knowledge representation).
Nhiệm vụ của bạn là chuẩn hóa tên các thực thể trong một đồ thị tri thức (knowledge graph) để đảm bảo tính nhất quán và thống nhất giữa các nút (entities).
Bạn cần phân tích NGỮ CẢNH từ các mối quan hệ (triples) để xác định chính xác các thực thể nào thực sự giống nhau.
"""

def get_entity_resolution_with_context_prompt(triples_text, entity_list):
    """
    Get entity resolution prompt WITH CONTEXT from triples.
    This helps LLM understand which entities refer to the same thing.
    """
    return f"""\
Dưới đây là các mối quan hệ (triples) được trích xuất từ văn bản gốc:
{triples_text}

Từ các triples trên, tôi đã trích xuất danh sách các thực thể sau:
{entity_list}

NHIỆM VỤ:
Dựa vào NGỮ CẢNH từ các triples, hãy xác định:
1. Các thực thể nào thực sự là CÙNG MỘT người/vật/khái niệm (ví dụ: "Minh", "anh ấy" có thể cùng chỉ một người)
2. Các thực thể nào là các biến thể của cùng một tên (ví dụ: "Donald Trump", "Trump", "Tổng thống Trump")
3. Các đại từ (anh ấy, cô ấy, nó, họ, người này, người đó) nên được thay thế bằng tên thực thể cụ thể

LƯU Ý QUAN TRỌNG:
- Phân tích KỸ các mối quan hệ để xác định đại từ chỉ ai/cái gì
- Ví dụ: "Minh là sinh viên. Anh ấy học tại HCMUT." → "anh ấy" = "Minh"
- CHỈ merge các tên mà chỉ đến cùng MỘT ENTITY dựa trên ngữ cảnh đã cho (là các EVENT)

Trả về JSON mapping:
{{
  "ENTITY|tên chuẩn hóa đầy đủ": ["ENTITY|variant 1", "ENTITY|variant 2", "ENTITY|đại từ tương ứng"],
  ...
}}

Ví dụ:
{{
  "ENTITY|nguyễn văn minh": ["ENTITY|minh", "ENTITY|anh ấy", "ENTITY|sinh viên này"],
  "ENTITY|đại học bách khoa": ["ENTITY|bách khoa", "ENTITY|trường", "ENTITY|đại học này"]
}}
"""

# Phase 3: Community relationship inference prompts

RELATIONSHIP_INFERENCE_SYSTEM_PROMPT = """\
Bạn là một cỗ máy chuyên gia trong biểu diễn tri thức (knowledge representation) và suy luận (inference).
Công việc của bạn là suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa (không được lặp lại ý nghĩa đã có sẵn) giữa các thực thể chưa được kết nối (disconnected entities) trong đồ thị tri thức (knowledge graph).
"""

def get_relationship_inference_user_prompt(entities1, entities2, triples_text):
    return f"""\
Cho một đồ thị tri thức (knowledge graph) với hai cộng đồng (community) bên dưới đây:

Thực thể trong Community 1: {entities1}
Thực thể trong Community 2: {entities2}

Đây là một số mối liên hệ có tồn tại trong đồ thị tri thức liên quan đến các thực thể trên:
{triples_text}

Xin hãy suy luận cẩn thận và chính xác từ 2 đến 3 mối liên hệ hợp lý giữa các thực thể từ Community 1 và các thực thể từ Community 2.
Nếu phát hiện được các yếu tố như địa điểm, thời gian trong các mối liên hệ suy luận được, hãy điền vào bên trong bộ năm. Tuy nhiên, phải CỰC KỲ CẨN TRỌNG và SUY LUẬN CHÍNH XÁC thông tin địa điểm, thời gian. TUYỆT ĐỐI không suy luận địa điểm, thời gian nếu không chắc chắn.

Trả lời kết quả dưới dạng danh sách JSON gồm các bộ năm đã suy luận được giống như bên dưới đây:
[
  {{
    "subject": "ENTITY|thực thể từ Community 1",
    "predicate": "mối liên hệ suy luận được",
    "object": "ENTITY|thực thể từ community 2"
  }},
  ...
]

QUAN TRỌNG:
- TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
- Chỉ bao gồm các mối liên hệ hợp lý và dễ dàng suy luận được, tức là mối liên hệ phải vô cùng RÕ RÀNG (clear predicates).
- Các mối liên hệ (predicates) suy luận được TUYỆT ĐỐI không vượt quá giới hạn TỐI ĐA 3 từ tiếng Việt (từ đơn, từ ghép, từ láy). Ưu tiên từ 1 đến 3 từ tiếng Việt nếu có thể.
- Sử dụng những cụm từ rõ ràng, dễ dàng diễn đạt mối liên hệ (predicates) suy luận được.
- Đảm bảo chủ ngữ, vị ngữ (subject, object) là các thực thể khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân) rối rắm.
- Toàn bộ BẮT BUỘC phải sử dụng tiếng Việt (nếu có thể).
"""

# Phase 4: Within-community relationship inference prompts
WITHIN_COMMUNITY_INFERENCE_SYSTEM_PROMPT = """\
Bạn là một cỗ máy chuyên gia trong biểu diễn tri thức (knowledge representation) và suy luận (inference).
Công việc của bạn là suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa (không được lặp lại ý nghĩa đã có sẵn) giữa các thực thể chưa được kết nối (disconnected entities) trong đồ thị tri thức (knowledge graph).
"""

def get_within_community_inference_user_prompt(pairs_text, triples_text):
    return f"""\
Cho một đồ thị tri thức (knowledge graph) có một số thực thể mặc dù liên quan nhau về mặt ngữ nghĩa nhưng lại chưa được kết nối trực tiếp trong đồ thị.

Sau đây là một số cặp thực thể mà có thể liên quan nhau:
{pairs_text}

Sau đây là một số mối liên hệ (predicates) có sẵn trong đồ thị tri thức mà liên quan đến các thực thể trên:
{triples_text}

Xin hãy suy luận các mối liên hệ hợp lý và thực sự có ý nghĩa (không lặp lại ý nghĩa đã có sẵn) giữa các cặp thực thể chưa được kết nối.
Trả về đáp án dưới dạng một mảng JSON của các bộ năm theo dạng như sau:
[
  {{
    "subject": "ENTITY|thực thể 1",
    "predicate": "mối liên hệ suy luận được",
    "object": "ENTITY|thực thể 2"
  }},
  ...
]

QUAN TRỌNG:
- TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
- Chỉ bao gồm các mối liên hệ hợp lý và dễ dàng suy luận được, tức là mối liên hệ phải vô cùng RÕ RÀNG (clear predicates).
- Các mối liên hệ (predicates) suy luận được TUYỆT ĐỐI không vượt quá giới hạn TỐI ĐA 3 từ tiếng Việt (từ đơn, từ ghép, từ láy). Ưu tiên từ 1 đến 3 từ tiếng Việt nếu có thể.
- Sử dụng những cụm từ rõ ràng, dễ dàng diễn đạt mối liên hệ (predicates) suy luận được.
- Đảm bảo chủ ngữ, vị ngữ (subject, object) là các thực thể khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân) rối rắm.
- Toàn bộ BẮT BUỘC phải sử dụng tiếng Việt (nếu có thể).
"""

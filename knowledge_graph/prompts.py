"""Centralized repository for all LLM prompts used in the knowledge graph system."""

# Phase 0: Pre-KG entity resolution
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

# Phase 1: Main extraction prompts

# MAIN_SYSTEM_PROMPT = """
# Bạn là một hệ thống AI tiên tiến, chuyên về trích xuất tri thức và sinh đồ thị tri thức (knowledge graph) cho ngôn ngữ tiếng Việt.
# Bạn có chuyên môn trong việc nhận diện các thực thể nhất quán và xác định các mối quan hệ có ý nghĩa trong văn bản.
# CHỈ DẪN QUAN TRỌNG: Tất cả các mối quan hệ (predicate) PHẢI có độ dài không quá 3 từ, lý tưởng nhất là 1-2 từ. Đây là quy định bắt buộc. Toàn bộ đầu ra phải bằng tiếng Việt.
# """

# MAIN_USER_PROMPT = """
# Nhiệm vụ của bạn: Đọc câu khẳng định dưới đây (được bao quanh bởi ba dấu ```), và xác định tất cả các mối quan hệ Chủ ngữ - Vị ngữ - Tân ngữ - Thời gian - Nơi chốn (S-P-O-T-L) trong câu đó. Sau đó, tạo ra một mảng JSON duy nhất gồm các đối tượng, mỗi đối tượng đại diện cho một bộ năm.
# Trong đó:
# - S (chủ ngữ) là thực thể chính trong câu.
# - P (vị ngữ) là hành động hoặc trạng thái liên kết chủ thể và đối tượng.
# - O (tân ngữ) là thực thể bị ảnh hưởng bởi hành động hoặc trạng thái.
# - T (thời gian) được hiểu là thời gian mà sự kiện xảy ra, hoặc thời điểm liên quan đến chủ thể và đối tượng. Ví dụ: ngày 12/10/1945, tháng 12, lúc 8 giờ sáng nay, lúc đoàn tàu vừa chạy qua.
# - L (nơi chốn) là địa điểm, vị trí, khu vực liên quan đến chủ thể và đối tượng. Ví dụ: Hà Nội, Việt Nam, trường Đại học Bách Khoa, khu vực Đông Nam Á, phòng làm việc của tôi.

# Hãy tuân thủ cẩn thận các quy tắc sau:
# - Tính nhất quán của thực thể (Entity Consistency): Sử dụng tên thực thể thống nhất trong toàn bộ câu khẳng định. Ví dụ, nếu "Nguyễn Hồng Minh" được nhắc đến là "Minh", "Ông Minh" hay "Hồng Minh" ở các chỗ khác nhau, hãy chỉ dùng một tên đầy đủ duy nhất ("nguyễn hồng minh") cho tất cả các bộ năm.
# - Thuật ngữ nguyên tử (Atomic Terms): Xác định rõ các khái niệm riêng biệt (ví dụ: vật thể, địa điểm, tổ chức, viết tắt, con người, điều kiện, khái niệm, cảm xúc). Tránh gộp nhiều ý vào cùng một thuật ngữ — mỗi thuật ngữ nên đơn nhất và rõ ràng.
# - Thay thế đại từ (Unified References): Thay thế các đại từ như "anh", "cô", "nó", "họ", v.v. bằng thực thể cụ thể nếu có thể xác định được.
# - Quan hệ cặp (Pairwise Relationships): Nếu có nhiều thực thể cùng xuất hiện trong một câu (hoặc đoạn ngắn có ngữ cảnh liên quan), hãy tạo bộ năm cho từng cặp có mối quan hệ có ý nghĩa.
# - CHỈ DẪN QUAN TRỌNG: Vị ngữ (predicate) PHẢI có độ dài từ 1 đến 3 từ. Tuyệt đối không vượt quá 3 từ. Giữ chúng thật ngắn gọn.
# - Đảm bảo rằng tất cả các mối quan hệ có thể nhận diện được trong văn bản đều được thể hiện trong các bộ năm S-P-O-T-L (O, T và L không nhất thiết phải có nhưng S-P phải có).
# - Chuẩn hóa thuật ngữ (Standardize Terminology): Nếu cùng một khái niệm xuất hiện với các biến thể khác nhau (ví dụ "trí tuệ nhân tạo" và "AI"), hãy sử dụng dạng phổ biến hoặc chuẩn nhất.
# - Viết toàn bộ nội dung S-P-O-T-L bằng chữ thường, bao gồm cả tên người và địa danh.
# - Nếu một người được nhắc đến theo tên, hãy tạo mối quan hệ đến địa điểm, nghề nghiệp, và điều mà họ nổi tiếng về (phát minh, viết, sáng lập, chức danh, v.v.) nếu có trong văn bản và phù hợp với ngữ cảnh.

# Lưu ý quan trọng:
# - Một câu có thể bao gồm nhiều bộ năm (S-P-O-T-L) nếu có nhiều mối quan hệ được thể hiện.
# - Hướng đến độ chính xác cao trong việc đặt tên thực thể — dùng các dạng tên cụ thể giúp phân biệt các thực thể tương tự nhau.
# - Tăng tính liên kết bằng cách sử dụng cùng tên thực thể cho cùng một khái niệm xuyên suốt câu.
# - Cân nhắc toàn bộ ngữ cảnh khi xác định thực thể và mối quan hệ.
# - TẤT CẢ CÁC VỊ NGỮ PHẢI DƯỚI 3 TỪ — ĐÂY LÀ YÊU CẦU BẮT BUỘC.
# - Không dùng các từ trừu tượng hoặc placeholder chung chung như "hành động", "sự kiện", "hiện tượng", v.v. Hãy chỉ rõ hành động hoặc sự kiện cụ thể trong ngữ cảnh. Nếu không xác định được, dùng cụm danh nghĩa mô tả nội dung thật (vd: "tăng trưởng dân số", "mở rộng đô thị") thay vì từ chung. Mục tiêu: mỗi triplet phải cụ thể, có thể hiểu độc lập, không mơ hồ.

# Yêu cầu đầu ra:
# - Không bao gồm bất kỳ văn bản hay chú thích nào ngoài phần JSON.
# - Chỉ trả về mảng JSON, trong đó mỗi phần tử là một đối tượng chứa "subject", "predicate", và "object".
# - Đảm bảo JSON hợp lệ và định dạng chính xác.

# Ví dụ:
# Tổng thống Donald Trump đã ký sắc lệnh hành pháp vào ngày 20 tháng 1 năm 2017 tại Washington D.C yêu cầu quân đội xâm lược Iran.
# [
#   {
#     "subject": "tổng thống donald trump",
#     "predicate": "ký",  // chỉ 2 từ
#     "object": "sắc lệnh hành pháp",
#     "time": "ngày 20 tháng 1 năm 2017",
#     "location": "washington d.c."
#   },
#   {
#     "subject": "sắc lệnh hành pháp",
#     "predicate": "yêu cầu",  // chỉ 1 từ
#     "object": "quân đội xâm lược iran",
#     "time": null,
#     "location": null
#   }
# ]

# Tiếng chuông điện thoại reo lên khi tôi đang làm việc tại phòng họp.
# [
#   {
#     "subject": "tiếng chuông điện thoại",
#     "predicate": "reo lên",  // chỉ 2 từ
#     "object": null,
#     "time": "khi tôi đang làm việc tại phòng họp."
#     "location": "null"
#   }
# ]

# Quan trọng: Chỉ xuất mảng JSON (chứa các đối tượng S-P-O-T-L), không có nội dung nào khác.

# Câu cần phân tích (nằm giữa ba dấu ```):
# """

MAIN_SYSTEM_PROMPT = """\
Bạn là một cỗ máy xử lý ngôn ngữ tự nhiên cực kỳ chính xác, được lập trình để phân tích văn bản tiếng Việt và chuyển đổi nó thành một đồ thị tri thức có cấu trúc.
Nhiệm vụ của bạn là đọc kỹ văn bản và trích xuất thực thể và các mối liên hệ để tạo thành các bộ năm (quintuple) một cách máy móc và nhất quán.
CHỈ DẪN QUAN TRỌNG: Tất cả các mối quan hệ (predicate) PHẢI có độ dài không quá 3 từ, lý tưởng nhất là 1-2 từ. Đây là quy định bắt buộc. Toàn bộ đầu ra phải bằng tiếng Việt.
"""

MAIN_USER_PROMPT = """\
MỤC TIÊU:
Trích xuất các bộ năm (quintuple) bao gồm: chủ ngữ (subject), vị ngữ (predicate), tân ngữ (object), địa điểm (location), và thời gian (time).

QUY TẮC QUAN TRỌNG VỀ VỊ NGỮ (PREDICATES):
Vị ngữ PHẢI có độ dài TỐI ĐA 3 từ tiếng Việt (từ đơn, từ phức, từ láy). Đây là yêu cầu quan trọng. Hãy chắt lọc hành động chính của câu thành một cụm động từ cực kỳ ngắn gọn. TUYỆT ĐỐI không dài hơn 3 từ tiếng Việt (từ đơn, từ phức, từ láy). Một số ví dụ: "là giám đốc công ty", "được yêu mến hết mực", "nuôi trồng", "ăn sạch sành sanh"...

QUY TẮC VỀ XỬ LÝ DỮ LIỆU:
HÃY CỐ GẮNG LẤY **TẤT CẢ** NGỮ CẢNH, **MỌI** THỰC THỂ VÀ MỐI LIÊN HỆ CÓ TRONG VĂN BẢN.

1. Nhất quán Thực thể (Entity Consistency):
- Các cụm từ (người, tổ chức, địa điểm, khái niệm, cảm xúc, viết tắt...) mà cùng ám chỉ một thực thể duy nhất thì phải được chuẩn hóa về một tên duy nhất.
- LƯU Ý CỰC KỲ QUAN TRỌNG: Khi chọn tên duy nhất, hãy lấy tên ĐẦY ĐỦ ý nghĩa nhất. TUYỆT ĐỐI KHÔNG DÙNG tên mang nghĩa chung chung, tổng quát như "nhà nước", "trạm xe"... mà cần viết cụ thể hơn "nhà nước của người Việt cổ", "trạm xe số 58"...
- Nếu chọn tên chuẩn hóa không tự tin, hãy SUY NGHĨ TỪNG BƯỚC và suy xét TẤT CẢ NGỮ CẢNH xung quanh để tìm ra tên thích hợp, đầy đủ ý nghĩa nhất, chi tiết nhất.
- Phải xem xét tất cả tên biến thể xuất hiện trong văn bản, bao gồm cả tên mã, chẳng hạn như ô tô ABA-170, nạn nhân MS003...
- Ví dụ: Nếu văn bản nhắc đến "Tập đoàn Vingroup", "Vingroup", và "VIC", bạn phải sử dụng một dạng duy nhất trong toàn bộ đầu ra, ví dụ: "Vingroup".
- Tương tự, "trí tuệ nhân tạo" và "AI" nên được chuẩn hóa thành "trí tuệ nhân tạo".

2. Giải quyết Tham chiếu (Reference Resolution):
- Thay thế tất cả các đại từ (ví dụ: "anh ấy", "cô nọ", "họ", "nó", "ông ta", "bà này", "công ty đó"...) bằng thực thể gốc mà nó đề cập đến. Nếu không xác định được, hãy bỏ qua đại từ đó.
- Ví dụ: Nếu văn bản là "Vàng là chú chó được yêu mến hết mực bởi ông Tài. Cậu ta luôn được ông cho ăn mỗi buổi sáng sau vườn nhà." thì "Cậu ta" đề cập đến "Vàng", còn "ông" đề cập đến "ông Tài". Bộ năm 1: (Vàng, là, chú chó, null, null). Bộ năm 2: (Vàng, được yêu mến bởi, Tài). Bộ năm 3: (Vàng, được cho ăn bởi, Tài, sau vườn, mỗi buổi sáng).

3. Thuật ngữ nguyên tử (Atomic Terms):
- Xác định rõ các khái niệm riêng biệt (ví dụ: vật thể, địa điểm, tổ chức, viết tắt, con người, điều kiện, khái niệm, cảm xúc).
- Tránh gộp nhiều ý vào cùng một thuật ngữ — mỗi thuật ngữ nên đơn nhất và rõ ràng.
- Ví dụ: "Ông An cùng bà Lan câu cá và trồng sau sau vườn", trong câu này nên hiểu "ông An" tách biệt với "bà Lan" thay vì "ông An cùng bà Lan", và "câu cá" tách biệt với "trồng sau" thay vì "cấu cá và trồng rau".
- Tuy nhiên, KHÔNG NÊN tách các vế cấu và mệnh đề phụ dùng để miêu tả địa điểm hoặc thời gian (như "tính từ lúc ông Lý lên ngôi vua" - miêu tả thời gian, "nếu chỉ nói xung quanh khu vực đô thị Hồ Chí Minh" - miêu tả địa điểm), các vế câu và mệnh đề phụ này nên được trích xuất toàn bộ vào thông tin địa điểm hoặc thời gian.
- Xin hãy cố gắng CẨN THẬN GIỮ Ý NGHĨA BAN ĐẦU của câu khi tách các thuật ngữ nguyên tử, nếu quá khó thì hãy SUY NGHĨ THEO TỪNG BƯỚC để trích xuất chính xác thuật ngữ nguyên tử mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.

4. Trích xuất Quan hệ Ngầm định (Implicit Relationship Extraction):
- Nếu văn bản giới thiệu một người cùng với chức danh, nghề nghiệp, hoặc công ty của họ (ví dụ: "Ông A, giám đốc công ty B, đã qua đời"), hãy tạo một bộ năm riêng để thể hiện mối quan hệ đó (thường với vị ngữ là "là").
- Ví dụ: Nếu văn bản là "Ông An, giám đốc công ty ABC, đã giải tán công ty vào năm 2008." thì nên có hai bộ năm. Bộ năm 1: (Ông An, là giám đốc, công ty ABC, null, null). Bộ năm 2 là (Ông An, giải tán, công ty ABC, null, năm 2008).
- Một số quan hệ ngầm định khi tách rời sẽ làm bộ năm lúc sau có nghĩa khác với câu ban đầu, xin hãy thật CẨN THẬN trích xuất các quan hệ ngầm định mà vẫn GIỮ LẠI ý nghĩa ban đầu của câu. Nếu quá khó, hãy SUY NGHĨ THEO TỪNG BƯỚC để trích xuất chính xác các quan hệ ngầm định mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.

5. Khai thác Thông tin Địa điểm (Location):
- Hãy cố gắng tìm kiếm thông tin địa điểm để bổ nghĩa cho vị ngữ (predicate). Nó miêu tả sự kiện (subject, predicate, object) đã xảy ra tại địa điểm nào (hoặc mốc miêu tả địa điểm).
- Khi phát hiện địa điểm (location) trong câu nói, xin đừng tách thành các bộ năm nhỏ hơn mà hãy viết thông tin location đầy đủ vào bộ năm hiện tại.
- Địa điểm có thể là một địa danh, địa chỉ cụ thể (ví dụ như đường Phạm Ngũ Lão, tỉnh Long Xuyên, vịnh Hạ Long...); hoặc có thể là nơi chốn được miêu tả tương đối (ví dụ như trước nhà, trong vườn, sau trường, dưới túp lều...); hoặc là một vế câu mệnh đề phụ miêu tả địa điểm (ví dụ: nếu tính từ Cà Mau đến vịnh Bắc Bộ, khi quan sát về phía đông dãy Bạch Mã...)
- Nếu không thể trích xuất địa điểm, hãy bỏ qua và điền giá trị null.
- Xin hãy cố gắng GIỮ LẠI Ý NGHĨA BAN ĐẦU của câu khi trích xuất thông tin địa điểm. Nếu quá khó, hãy SUY NGHĨ TỪNG BƯỚC để trích xuất địa điểm mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.

6. Khai thác Thông tin Thời gian (Time):
- Hãy cố gắng tìm kiếm thông tin thời gian để bổ nghĩa cho vị ngữ (predicate). Nó miêu tả sự kiện (subject, predicate, object) đã xảy ra tại thời điểm nào (hoặc mốc miêu tả thời gian).
- Khi phát hiện thời gian (time) trong câu nói, xin đừng tách thành các bộ năm nhỏ hơn mà hãy viết thông tin time đầy đủ vào bộ năm hiện tại.
- Thời gian có thể là một thời điểm, ngày lễ cụ thể (ví dụ như 18:30, giữa trưa 12:00, vào thứ 5, vào ngày 13 tháng 5, năm 2004, những ngày lễ Trung Thu, 3 ngày Tết...); hoặc có thể được miêu tả tương đối (ví dụ như mỗi buổi tối, rạng sáng mỗi thứ hai, hằng đêm...) hoặc có thể liên quan đến sự kiện khác (ví dụ như sau khi chủ tịch chết, trước khi Hồ Chí Minh về Việt Nam, trong khi bom hạt nhân rơi xuống Hiroshima...); hoặc là một vế câu hoặc mệnh đề phụ miêu tả thời gian (ví dụ: nếu tính từ khi nhà vua ra đời, về khoảng thời gian khi Lý Thái Tổ vẫn cai quản nước Nam...)
- Nếu không thể trích xuất thời gian, hãy bỏ qua và điền giá trị null.
- Xin hãy cố gắng GIỮ LẠI Ý NGHĨA BAN ĐẦU của câu khi trích xuất thông tin thời gian. Nếu quá khó, hãy SUY NGHĨ TỪNG BƯỚC để trích xuất thời gian mà vẫn GIỮ Ý NGHĨA BAN ĐẦU.

QUY TẮC VỀ ĐỊNH DẠNG ĐẦU RA:
1. Định dạng JSON: Đầu ra PHẢI là một danh sách JSON hợp lệ []. Mỗi phần tử là một đối tượng {} chứa 5 trường: "subject", "predicate", "object", "location", "time".
2. Giá trị Rỗng (null): Nếu một thành phần không có trong câu, hãy sử dụng giá trị null.
3. Viết thường Toàn bộ: TẤT CẢ các giá trị văn bản trong các trường subject, predicate, object, location, time phải được chuyển thành chữ thường (lowercase).
4. Không có Dữ liệu Thừa: Chỉ trả về danh sách JSON. TUYỆT ĐỐI không kèm theo bất kỳ lời giải thích hay văn bản nào khác.

Lưu ý QUAN TRỌNG:
- Hướng đến độ chính xác cao trong việc đặt tên thực thể — dùng các dạng tên cụ thể giúp phân biệt các thực thể tương tự nhau.
- Tăng tính liên kết bằng cách sử dụng cùng tên thực thể cho cùng một khái niệm xuyên suốt câu.
- Cân nhắc toàn bộ ngữ cảnh khi xác định thực thể và mối quan hệ, phải đọc đi đọc lại thật kỹ toàn bộ ngữ cảnh, văn bản đã cho.
- TẤT CẢ CÁC VỊ NGỮ PHẢI DƯỚI 3 TỪ — ĐÂY LÀ YÊU CẦU BẮT BUỘC.
- Không dùng các từ trừu tượng hoặc placeholder chung chung như "hành động", "sự kiện", "hiện tượng"... Hãy chỉ rõ hành động hoặc sự kiện cụ thể trong ngữ cảnh. Nếu không xác định được, dùng cụm danh nghĩa mô tả nội dung thật (vd: "tăng trưởng dân số", "mở rộng đô thị") thay vì từ chung. Mục tiêu: mỗi triplet phải cụ thể, có thể hiểu độc lập, không mơ hồ.
- TUYỆT ĐỐI KHÔNG điền giá trị null vào các trường như subject, predicate; tuy nhiên, hoàn toàn có thể sử dụng giá trị null cho các trường như object, location, time.
- PHẢI SUY NGHĨ THEO TỪNG BƯỚC để phân tích cấu trúc câu phức tạp, từ đó xác định rõ đâu là mệnh đề chính và mệnh đề phụ, cuối cùng là trích xuất các bộ năm có thể có từ cấu trúc câu đã hiểu rõ.

Dựa trên vai trò và các quy tắc nghiêm ngặt đã được hướng dẫn, hãy trích xuất các bộ năm từ các văn bản, bên dưới là một số ví dụ minh họa.

VÍ DỤ:

Văn bản 1:
"Olympic Sinh học quốc tế (tiếng Anh: International Biology Olympiad, tên viết tắt là IBO) là một kỳ thi Olympic khoa học dành cho học sinh trung học phổ thông. Ngôn ngữ chính thức của IBO là tiếng Anh. Các Olympic quốc tế về học thuật đã lần lượt ra đời dưới sự bảo trợ của Liên Hợp Quốc vào thập niên 1960 (lúc đầu chủ yếu ở Đông Âu)."
Đầu ra 1:
[
  {
    "subject": "olympic sinh học quốc tế",
    "predicate": "là",
    "object": "kỳ thi olympic khoa học",
    "time": null
    "location": null,
  },
  {
    "subject": "olympic sinh học quốc tế",
    "predicate": "dành cho",
    "object": "học sinh trung học phổ thông",
    "time": null
    "location": null,
  },
  {
    "subject": "ngôn ngữ chính thức của olympic sinh học quốc tế",
    "predicate": "là",
    "object": "tiếng anh",
    "time": null
    "location": null,
  },
  {
    "subject": "olympic quốc tế về học thuật",
    "predicate": "ra đời dưới sự bảo trợ của",
    "object": "liên hợp quốc",
    "time": "thập niên 1960",
    "location": null,
  },
  {
    "subject": "olympic quốc tế về học thuật",
    "predicate": "ra đời chủ yếu ở",
    "object": "châu âu",
    "time": "lúc đầu",
    "location": null,
  }
]

Văn bản 2:
"Từ năm 2019, tại OpenAI, sự xuất hiện của các mô hình ngôn ngữ dựa trên kiến trúc transformer và được huấn luyện trước đã cho phép tạo ra văn bản mạch lạc, có tính tự nhiên cao."
Đầu ra 2:
[
  {
    "subject": "mô hình ngôn ngữ",
    "predicate": "cho phép tạo ra",
    "object": "văn bản tự nhiên",
    "time": "năm 2019"
    "location": "tại openai",
  },
  {
    "subject": "mô hình ngôn ngữ",
    "predicate": "dựa trên",
    "object": "kiến trúc transformer",
    "time": "năm 2019"
    "location": "tại openai",
  },
  {
    "subject": "mô hình ngôn ngữ",
    "predicate": "được huấn luyện trước bởi",
    "object": "openai",
    "time": "năm 2019"
    "location": null,
  }
]

Văn bản 3:
"Donald Trump trồng rau tại nơi bà ông từng sống sau khi ông về hưu."
Đầu ra 3:
[
  {
    subject: "Donald Trump",
    predicate: "trồng",
    object: "rau",
    time: "sau khi ông về hưu",
    location: "nơi bà ông từng sống"
  }
]

YÊU CẦU:
Bây giờ, hãy phân tích văn bản dưới đây và trả về kết quả dưới dạng danh sách JSON.
Văn bản cần phân tích và trích xuất (nằm giữa cặp ba dấu ngoặc ngược, triple backticks, ```):
"""

def get_normalize_entity_prompt(text):
    prompt = f"""
Bạn là một trợ lý ngôn ngữ thông minh.  

Nhiệm vụ của bạn là **chuẩn hóa tất cả các thực thể** trong văn bản, thuộc về các thành phần context, prompt, response.  

Các yêu cầu:  
- Mọi từ hoặc cụm từ **chỉ cùng một thực thể** (bao gồm tên đầy đủ, biệt danh, đại từ, các cách viết tắt, alias, nickname...) phải được thay thế bằng **một tên chuẩn hóa duy nhất**.  
- Tên chuẩn hóa nên là **tên đầy đủ, rõ ràng và dễ nhận biết**.
- Giữ nguyên ngữ cảnh và các từ khác trong văn bản, chỉ thay thế từ/biến thể của thực thể đó.  
- Không thay đổi các thực thể khác, chỉ nhóm các biến thể của cùng một thực thể.

**Ví dụ:**  

Văn bản gốc:  
"
context: Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa. Trong đó, hiến chương này cũng nói rằng đất nước này không được thực hiện chính sách thực dân.
prompt: Hiến chương Pháp ngữ 1977 quy định Pháp là nước gì?
response: Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa.
"  

Văn bản sau chuẩn hóa:  
"
context: Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa. Trong đó, Hiến chương Pháp ngữ 1977 này cũng nói rằng nước Pháp không được thực hiện chính sách thực dân.
prompt: Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước gì?
response: Hiến chương Pháp ngữ 1977 quy định nước Pháp là nước Cộng hòa.
"

---

**Nhiệm vụ của bạn:**  
Nhận một văn bản đầu vào và trả về văn bản mới **đã chuẩn hóa tất cả các thực thể** theo yêu cầu trên.

Văn bản cần phân tích (nằm giữa ba dấu ```):
{text}
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
- Đầu ra chỉ viết các câu khẳng định (claim) đã trích xuất được, không thêm các chi tiết bên ngoài như luồng suy nghĩ, đánh giá thêm...

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

def get_main_user_prompt(text):
    return MAIN_USER_PROMPT + f"```{text}```"

# Phase 2: Entity standardization prompts

ENTITY_RESOLUTION_SYSTEM_PROMPT = """\
Bạn là một chuyên gia trong lĩnh vực nhận dạng và hợp nhất thực thể (entity resolution) cũng như biểu diễn tri thức (knowledge representation).
Nhiệm vụ của bạn là chuẩn hóa tên các thực thể trong một đồ thị tri thức (knowledge graph) để đảm bảo tính nhất quán và thống nhất giữa các nút (entities).
Bạn cần phân tích NGỮ CẢNH từ các mối quan hệ (triples) để xác định chính xác các thực thể nào thực sự giống nhau.
"""

def get_entity_resolution_user_prompt(entity_list):
    return f"""\
Dưới đây là danh sách các tên thực thể được trích xuất từ một đồ thị tri thức.
Một số tên có thể cùng chỉ về một thực thể trong thế giới thực nhưng được diễn đạt bằng những cách khác nhau.

Hãy xác định các nhóm thực thể đề cập đến cùng một khái niệm hoặc thực thể, 
và cung cấp **một tên chuẩn hóa duy nhất** cho mỗi nhóm.

Trả kết quả của bạn dưới dạng **đối tượng JSON**, trong đó:
- **Khóa (key)** là tên chuẩn hóa, tên đầy đủ nhất cho thực thể đó.
- **Giá trị (value)** là danh sách các biến thể (variant) của tên đó.

Chỉ bao gồm những thực thể có nhiều biến thể hoặc cần chuẩn hóa tên.

Danh sách thực thể:
{entity_list}

Định dạng kết quả JSON hợp lệ như sau:
{{
  "tên chuẩn hóa 1": ["biến thể 1", "biến thể 2"],
  "tên chuẩn hóa 2": ["biến thể 3", "biến thể 4", "biến thể 5"]
}}
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
- CHỈ merge các entities THỰC SỰ giống nhau dựa trên ngữ cảnh

Trả về JSON mapping:
{{
  "Tên chuẩn hóa đầy đủ": ["variant 1", "variant 2", "đại từ tương ứng"],
  ...
}}

Ví dụ:
{{
  "Nguyễn Văn Minh": ["minh", "anh ấy", "sinh viên này"],
  "Đại học Bách Khoa": ["bách khoa", "trường", "đại học này"]
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
    "subject": "thực thể từ Community 1",
    "predicate": "mối liên hệ suy luận được",
    "object": "thực thể từ community 2",
    "location": "địa điểm suy luận được" hoặc null,
    "time": "thời gian suy luận được" hoặc null
  }},
  ...
]

QUAN TRỌNG:
TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
Chỉ bao gồm các mối liên hệ hợp lý và dễ dàng suy luận được, tức là mối liên hệ phải vô cùng RÕ RÀNG (clear predicates).
Các mối liên hệ (predicates) suy luận được TUYỆT ĐỐI không vượt quá giới hạn TỐI ĐA 3 từ tiếng Việt (từ đơn, từ ghép, từ láy). Ưu tiên từ 1 đến 3 từ tiếng Việt nếu có thể.
Sử dụng những cụm từ rõ ràng, dễ dàng diễn đạt mối liên hệ (predicates) suy luận được.
Đảm bảo chủ ngữ, vị ngữ (subject, object) là các thực thể khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân) rối rắm.
Toàn bộ BẮT BUỘC phải sử dụng tiếng Việt (nếu có thể).
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
    "subject": "thực thể 1",
    "predicate": "mối liên hệ suy luận được",
    "object": "thực thể 2",
    "location": "địa điểm suy luận được" hoặc null,
    "time": "thời gian suy luận được" hoặc null
  }},
  ...
]

QUAN TRỌNG:
TUYỆT ĐỐI không để trống hoặc viết giá trị null vào các trường chủ ngữ (subject), vị ngữ (predicate), và tân ngữ (object).
Chỉ bao gồm các mối liên hệ hợp lý và dễ dàng suy luận được, tức là mối liên hệ phải vô cùng RÕ RÀNG (clear predicates).
Các mối liên hệ (predicates) suy luận được TUYỆT ĐỐI không vượt quá giới hạn TỐI ĐA 3 từ tiếng Việt (từ đơn, từ ghép, từ láy). Ưu tiên từ 1 đến 3 từ tiếng Việt nếu có thể.
Sử dụng những cụm từ rõ ràng, dễ dàng diễn đạt mối liên hệ (predicates) suy luận được.
Đảm bảo chủ ngữ, vị ngữ (subject, object) là các thực thể khác nhau, tránh việc tự tham chiếu (tham chiếu bản thân) rối rắm.
Toàn bộ BẮT BUỘC phải sử dụng tiếng Việt (nếu có thể).
"""

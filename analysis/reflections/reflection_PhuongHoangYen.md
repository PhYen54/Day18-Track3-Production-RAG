# Individual Reflection — Lab 18

**Tên:** Phương Hoàng Yến  
**Module phụ trách:** M4 + M5

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M4, M5
- Các hàm/class chính đã viết: evaluate_ragas, failure_analysis, summarize_chunk, generate_hypothesis_questions, contextual_prepend, extract_metadata,  enrich_chunks
- Số tests pass: 4/4 (M4), 10/10 (M5)
```bash
(venv) C:\Users\tc\Documents\Day18-Track3-Production-RAG\tests>pytest test_m4.py
=========================================== test session starts ===========================================
platform win32 -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\tc\Documents\Day18-Track3-Production-RAG\tests
plugins: anyio-4.13.0
collected 4 items                                                                                         

test_m4.py ....                                                                                      [100%]

============================================ 4 passed in 0.09s ============================================
```bash
(venv) C:\Users\tc\Documents\Day18-Track3-Production-RAG\tests>pytest test_m5.py
=========================================== test session starts ===========================================
platform win32 -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\tc\Documents\Day18-Track3-Production-RAG\tests
plugins: anyio-4.13.0
collected 10 items                                                                                         

test_m5.py ..........                                                                                [100%]

=========================================== 10 passed in 0.08s ============================================
```
## 2. Kiến thức học được

- Khái niệm mới nhất:

Cơ chế Hybrid Search kết hợp giữa tìm kiếm từ khóa (BM25/Sparse Vector) và tìm kiếm ngữ nghĩa (Dense Vector) thông qua thuật toán gộp điểm RRF (Reciprocal Rank Fusion). Cùng với đó là chiến lược tối ưu hóa lúc đưa dữ liệu vào DB (Ingestion): Dùng UUID băm từ nội dung text để tạo ID duy nhất (tránh ghi đè/trùng lặp vector) và kỹ thuật Batching (chia nhỏ dữ liệu) để chống tràn RAM, nghẽn mạng.

- Điều bất ngờ nhất:

Lỗi từ chối kết nối kinh điển [WinError 10061] (Connection Refused) và lỗi 404 Not Found hóa ra không nằm ở logic code Python hay do Qdrant bị hỏng, mà nằm ở cơ chế mạng (networking) giữa Windows và Docker. Script Python chạy ở môi trường ngoài (host) không thể dùng cấu hình 0.0.0.0 hay tên service Docker ("qdrant") để giao tiếp, mà bắt buộc phải trỏ chính xác về localhost thì hai bên mới "nhìn thấy" nhau.

- Kết nối với bài giảng (slide nào):

Liên quan đến phần Kiến trúc hệ thống RAG (RAG Architecture) và Cơ sở dữ liệu Vector (Vector Database) (Slide 17)
## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất:

Lỗi mạng giao tiếp (Networking) giữa môi trường host Windows (nơi chạy script Python) và container Docker (nơi chạy cơ sở dữ liệu Qdrant). Cụ thể là chuỗi lỗi 404 Not Found (do chưa có dữ liệu) dẫn đến lỗi cấu hình [WinError 10061] Connection refused (máy chủ từ chối kết nối). Nguyên nhân sâu xa là do file config khai báo host là 0.0.0.0 (hoặc tên service Docker), khiến Windows không thể định tuyến gói tin đến đúng cổng 6333 của container trên localhost.

- Cách giải quyết:

Dùng Web UI và lệnh docker ps để xác nhận chắc chắn Qdrant container vẫn đang sống và đã mở port 6333.

Viết một script test độc lập (test_connect.py) để khoanh vùng nguyên nhân (xác định lỗi do code hay do Docker).

Chỉnh sửa class DenseSearch, bỏ qua biến môi trường bị lỗi và ép cứng (hardcode) URL kết nối về http://localhost:6333 để tạo cầu nối trực tiếp.

Tái cấu trúc lại hàm index(): Thay lệnh xóa bộ sưu tập (recreate_collection) bằng lệnh kiểm tra (collection_exists) để bảo toàn dữ liệu cũ, đồng thời áp dụng UUID và cơ chế Batching để tránh lỗi khi nạp dữ liệu lớn.

- Thời gian debug: khoảng 45p

## 4. Nếu làm lại

- Sẽ làm khác điều gì: sẽ chạy docker và test qdrant riêng xem có kết nối được không trước khi bỏ vào đoạn code chung
- Module nào muốn thử tiếp:  m2

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |

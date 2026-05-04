# Failure Analysis — Lab 18: Production RAG

**Nhóm:** TBD  
**Thành viên:** TBD (M1) · TBD (M2) · TBD (M3) · TBD (M4)

---

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 0.6590 | 0.6753 | +0.0164 |
| Answer Relevancy | 0.7262 | 0.6921 | -0.0341 |
| Context Precision | 1.0000 | 1.0000 | +0.0000 |
| Context Recall | 0.9362 | 0.8402 | -0.0960 |

## Bottom-5 Failures

### #1
- **Question:** Chủ thể dữ liệu có những quyền gì theo Điều 9 Nghị định 13/2023?
- **Expected:** Quyền được biết, quyền đồng ý, quyền truy cập, quyền rút lại sự đồng ý, quyền xóa dữ liệu, quyền hạn chế xử lý dữ liệu, quyền cung cấp dữ liệu, quyền phản đối xử lý dữ liệu, quyền khiếu nại tố cáo khởi kiện, quyền yêu cầu bồi thường thiệt hại, quyền tự bảo vệ
- **Got:** Not stored (LLM answer not logged)
- **Worst metric:** faithfulness (0.0000)
- **Error Tree:** Output sai → Context đúng? (can verify) → Query OK? yes → Fix at generation
- **Root cause:** Long list answer; model likely paraphrased or omitted required items
- **Suggested fix:** Use extractive prompt with bullet list and require quotes from context

### #2
- **Question:** Thuế GTGT phát sinh trong kỳ của DHA Surfaces được tính như thế nào?
- **Expected:** Bằng thuế GTGT đầu ra trừ thuế GTGT đầu vào được khấu trừ: 344.675.400 - 215.163.767 = 129.511.633 đồng
- **Got:** Not stored (LLM answer not logged)
- **Worst metric:** faithfulness (0.0000)
- **Error Tree:** Output sai → Context đúng? likely → Query OK? yes → Fix at generation
- **Root cause:** Numeric calculation not enforced; model may answer without exact numbers
- **Suggested fix:** Add calc template and force numeric extraction from context

### #3
- **Question:** Thuế GTGT phải nộp trong kỳ của DHA Surfaces là bao nhiêu?
- **Expected:** 52.133.830 đồng
- **Got:** Not stored (LLM answer not logged)
- **Worst metric:** faithfulness (0.0000)
- **Error Tree:** Output sai → Context đúng? likely → Query OK? yes → Fix at generation
- **Root cause:** Exact numeric value not captured
- **Suggested fix:** Require answer as a single number with currency

### #4
- **Question:** Người ký tờ khai thuế GTGT của DHA Surfaces là ai?
- **Expected:** Trịnh Thị Sang
- **Got:** Not stored (LLM answer not logged)
- **Worst metric:** faithfulness (0.0000)
- **Error Tree:** Output sai → Context đúng? verify → Query OK? yes → Fix at retrieval or generation
- **Root cause:** Name entity not surfaced in top contexts
- **Suggested fix:** Increase top_k, add entity-aware rerank, or prioritize fields like signer

### #5
- **Question:** Dữ liệu cá nhân nhạy cảm là gì theo Nghị định 13/2023?
- **Expected:** Là dữ liệu cá nhân gắn liền với quyền riêng tư của cá nhân mà khi bị xâm phạm sẽ gây ảnh hưởng trực tiếp tới quyền và lợi ích hợp pháp của cá nhân, bao gồm quan điểm chính trị, tôn giáo, sức khỏe, đời tư, nguồn gốc chủng tộc, đặc điểm di truyền, sinh học, đời sống tình dục, dữ liệu tội phạm, thông tin tài khoản ngân hàng, dữ liệu vị trí và các dữ liệu đặc thù khác theo pháp luật
- **Got:** Not stored (LLM answer not logged)
- **Worst metric:** faithfulness (0.4394)
- **Error Tree:** Output sai → Context đúng? likely → Query OK? yes → Fix at generation
- **Root cause:** Long definition; partial or paraphrased answer
- **Suggested fix:** Use extractive summary with required key phrases

## Case Study (cho presentation)

**Question chọn phân tích:** Thuế GTGT phát sinh trong kỳ của DHA Surfaces được tính như thế nào?

**Error Tree walkthrough:**
1. Output đúng? → No
2. Context đúng? → Likely yes (numbers appear in doc; verify)
3. Query rewrite OK? → Yes
4. Fix ở bước: Generation (force numeric extraction + formula)

**Nếu có thêm 1 giờ, sẽ optimize:**
- Log LLM answers + contexts to JSON for analysis
- Add extractive prompt and numeric parser for tax questions
- Increase rerank top_k and add entity-aware scoring for names

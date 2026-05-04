# Individual Reflection — Lab 18

**Tên:** Nguyễn Minh Châu
**Module phụ trách:** M3

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M3 Rerank (Reranking with Cross-Encoder and Benchmarking)
- Các hàm/class chính đã viết: CrossEncoderReranker.rerank(), FlashrankReranker.rerank(), benchmark_reranker()
- Số tests pass: 4/4

## 2. Kiến thức học được

- Khái niệm mới nhất: Cross-encoder reranking for improving retrieval quality by re-scoring query-document pairs, and latency benchmarking to measure performance in production RAG systems.
- Điều bất ngờ nhất: How cross-encoders can significantly improve relevance over initial retrieval, but at the cost of higher latency, requiring careful benchmarking.
- Kết nối với bài giảng (slide nào): Slides on advanced retrieval techniques, reranking strategies, and performance optimization in RAG pipelines.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Integrating the cross-encoder model and ensuring it handles Vietnamese text properly; also, accurately measuring latency with multiple runs.
- Cách giải quyết: Used FlagReranker for cross-encoder implementation and time.perf_counter() for precise timing; tested with sample queries to validate reranking effectiveness.
- Thời gian debug: Approximately 40 minutes on model loading and ensuring reranked results are correctly sorted by score.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Would explore more lightweight reranking models to reduce latency and add GPU acceleration for faster inference.
- Module nào muốn thử tiếp: M4 Eval, to understand evaluation metrics in RAG systems.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 4 |
| Code quality | 4 |
| Teamwork | 5 |
| Problem solving | 4 |

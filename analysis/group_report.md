# Group Report — Lab 18: Production RAG

**Nhóm:** TBD  
**Ngày:** 2026-05-04

## Thành viên & Phân công

| Tên | Module | Hoàn thành | Tests pass |
|-----|--------|-----------|-----------|
| TBD | M1: Chunking | Yes | 13/13 |
| TBD | M2: Hybrid Search | Yes | 5/5 |
| TBD | M3: Reranking | Yes | 5/5 |
| TBD | M4: Evaluation | Yes | 4/4 |

## Kết quả RAGAS

| Metric | Naive | Production | Δ |
|--------|-------|-----------|---|
| Faithfulness | 0.6590 | 0.6753 | +0.0164 |
| Answer Relevancy | 0.7262 | 0.6921 | -0.0341 |
| Context Precision | 1.0000 | 1.0000 | +0.0000 |
| Context Recall | 0.9362 | 0.8402 | -0.0960 |

## Key Findings

1. **Biggest improvement:** Faithfulness improved slightly (+0.0164) after using the LLM answer.
2. **Biggest challenge:** Answer relevancy and context recall dropped vs baseline; prompt and retrieval need tuning.
3. **Surprise finding:** Baseline outperformed production on answer relevancy and recall despite rerank/enrichment.

## Presentation Notes (5 phút)

1. RAGAS scores (naive vs production): faith 0.6590 -> 0.6753, relevancy 0.7262 -> 0.6921, recall 0.9362 -> 0.8402.
2. Biggest win — module nào, tại sao: M3 + LLM answer improved faithfulness slightly.
3. Case study — 1 failure, Error Tree walkthrough: "Thuế GTGT phát sinh trong kỳ..."; fail at generation (numeric extraction).
4. Next optimization nếu có thêm 1 giờ: log answers + contexts; enforce extractive numeric templates; tune top_k/rerank.

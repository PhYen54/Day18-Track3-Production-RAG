"""Module 3: Reranking — Cross-encoder top-20 → top-3 + latency benchmark."""

import os, sys, time
from dataclasses import dataclass
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def _load_model(self):
        # For OpenAI, client is already initialized in __init__
        return self.client

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        # TODO 2: CrossEncoderReranker.rerank() — use OpenAI to score documents
        client = self._load_model()
        
        # Score each document using OpenAI
        scored_docs = []
        for doc in documents:
            prompt = f"""Rate the relevance of the following document to the query on a scale of 0 to 10.
Query: {query}
Document: {doc["text"]}
Respond with only a number (0-10)."""
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
            except (ValueError, IndexError):
                score = 0.0
            
            scored_docs.append((score, doc))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Return top-k results
        results = []
        for i, (score, doc) in enumerate(scored_docs[:top_k]):
            results.append(RerankResult(
                text=doc["text"],
                original_score=doc["score"],
                rerank_score=score,
                metadata=doc["metadata"],
                rank=i+1
            ))
        return results


class FlashrankReranker:
    """Lightweight alternative using OpenAI's faster model."""
    def __init__(self, model_name: str = "gpt-4o-mini", api_key: str = None):
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        # TODO (optional): Use lightweight OpenAI model for faster reranking
        try:
            scored_docs = []
            for doc in documents:
                prompt = f"""Rate relevance (0-10):
Query: {query}
Doc: {doc["text"]}
Answer: number only"""
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                
                try:
                    score = float(response.choices[0].message.content.strip())
                except (ValueError, IndexError):
                    score = 0.0
                
                scored_docs.append((score, doc))
            
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for i, (score, doc) in enumerate(scored_docs[:top_k]):
                results.append(RerankResult(
                    text=doc["text"],
                    original_score=doc["score"],
                    rerank_score=score,
                    metadata=doc["metadata"],
                    rank=i+1
                ))
            return results
        except Exception:
            return []


def benchmark_reranker(reranker, query: str, documents: list[dict], n_runs: int = 5) -> dict:
    """Benchmark latency over n_runs."""
    # TODO: Implement benchmark
    # 1. times = []
    # 2. for _ in range(n_runs):
    #      start = time.perf_counter()
    #      reranker.rerank(query, documents)
    #      times.append((time.perf_counter() - start) * 1000)  # ms
    # 3. return {"avg_ms": mean(times), "min_ms": min(times), "max_ms": max(times)}
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        reranker.rerank(query, documents)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms
    return {
        "avg_ms": sum(times) / len(times),
        "min_ms": min(times),
        "max_ms": max(times)
    }


if __name__ == "__main__":
    query = "Nhân viên được nghỉ phép bao nhiêu ngày?"
    docs = [
        {"text": "Nhân viên được nghỉ 12 ngày/năm.", "score": 0.8, "metadata": {}},
        {"text": "Mật khẩu thay đổi mỗi 90 ngày.", "score": 0.7, "metadata": {}},
        {"text": "Thời gian thử việc là 60 ngày.", "score": 0.75, "metadata": {}},
    ]
    reranker = CrossEncoderReranker()
    for r in reranker.rerank(query, docs):
        print(f"[{r.rank}] {r.rerank_score:.4f} | {r.text}")

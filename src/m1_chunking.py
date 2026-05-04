"""
Module 1: Advanced Chunking Strategies
=======================================
Implement semantic, hierarchical, và structure-aware chunking.
So sánh với basic chunking (baseline) để thấy improvement.

Test: pytest tests/test_m1.py
"""

import os, sys, glob, re, math
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (DATA_DIR, HIERARCHICAL_PARENT_SIZE, HIERARCHICAL_CHILD_SIZE,
                    SEMANTIC_THRESHOLD)


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load all markdown/text files from data/. (Đã implement sẵn)"""
    docs = []
    for fp in sorted(glob.glob(os.path.join(data_dir, "*.md"))):
        with open(fp, encoding="utf-8") as f:
            docs.append({"text": f.read(), "metadata": {"source": os.path.basename(fp)}})
    return docs


# ─── Baseline: Basic Chunking (để so sánh) ──────────────


def chunk_basic(text: str, chunk_size: int = 500, metadata: dict | None = None) -> list[Chunk]:
    """
    Basic chunking: split theo paragraph (\\n\\n).
    Đây là baseline — KHÔNG phải mục tiêu của module này.
    (Đã implement sẵn)
    """
    metadata = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for i, para in enumerate(paragraphs):
        if len(current) + len(para) > chunk_size and current:
            chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
            current = ""
        current += para + "\n\n"
    if current.strip():
        chunks.append(Chunk(text=current.strip(), metadata={**metadata, "chunk_index": len(chunks)}))
    return chunks


# ─── Strategy 1: Semantic Chunking ───────────────────────


def chunk_semantic(text: str, threshold: float = SEMANTIC_THRESHOLD,
                   metadata: dict | None = None) -> list[Chunk]:
    """
    Split text by sentence similarity — nhóm câu cùng chủ đề.
    Tốt hơn basic vì không cắt giữa ý.

    Args:
        text: Input text.
        threshold: Cosine similarity threshold. Dưới threshold → tách chunk mới.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects grouped by semantic similarity.
    """
    metadata = metadata or {}
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\n+", text) if s.strip()]
    if not sentences:
        return []

    def cosine_sim(a, b) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    embeddings = None
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(sentences)
    except Exception:
        embeddings = None

    def simple_sim(a_text: str, b_text: str) -> float:
        a_tokens = set(re.findall(r"\w+", a_text.lower()))
        b_tokens = set(re.findall(r"\w+", b_text.lower()))
        if not a_tokens or not b_tokens:
            return 0.0
        return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)

    chunks: list[Chunk] = []
    current_group = [sentences[0]]
    for i in range(1, len(sentences)):
        if embeddings is not None:
            sim = cosine_sim(embeddings[i - 1], embeddings[i])
        else:
            sim = simple_sim(sentences[i - 1], sentences[i])

        if sim < threshold:
            chunks.append(Chunk(
                text=" ".join(current_group).strip(),
                metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"},
            ))
            current_group = []
        current_group.append(sentences[i])

    if current_group:
        chunks.append(Chunk(
            text=" ".join(current_group).strip(),
            metadata={**metadata, "chunk_index": len(chunks), "strategy": "semantic"},
        ))

    return chunks


# ─── Strategy 2: Hierarchical Chunking ──────────────────


def chunk_hierarchical(text: str, parent_size: int = HIERARCHICAL_PARENT_SIZE,
                       child_size: int = HIERARCHICAL_CHILD_SIZE,
                       metadata: dict | None = None) -> tuple[list[Chunk], list[Chunk]]:
    """
    Parent-child hierarchy: retrieve child (precision) → return parent (context).
    Đây là default recommendation cho production RAG.

    Args:
        text: Input text.
        parent_size: Chars per parent chunk.
        child_size: Chars per child chunk.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        (parents, children) — mỗi child có parent_id link đến parent.
    """
    metadata = metadata or {}
    parents: list[Chunk] = []
    children: list[Chunk] = []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) > parent_size:
            pid = f"parent_{len(parents)}"
            parent_chunk = Chunk(
                text=current.strip(),
                metadata={**metadata, "chunk_type": "parent", "parent_id": pid, "chunk_index": len(parents)},
            )
            parents.append(parent_chunk)
            current = ""
        current += para + "\n\n"

    if current.strip():
        pid = f"parent_{len(parents)}"
        parents.append(Chunk(
            text=current.strip(),
            metadata={**metadata, "chunk_type": "parent", "parent_id": pid, "chunk_index": len(parents)},
        ))

    for parent in parents:
        pid = parent.metadata.get("parent_id")
        parent_text = parent.text
        for start in range(0, len(parent_text), child_size):
            child_text = parent_text[start:start + child_size].strip()
            if not child_text:
                continue
            children.append(Chunk(
                text=child_text,
                metadata={**metadata, "chunk_type": "child", "parent_id": pid, "chunk_index": len(children)},
                parent_id=pid,
            ))

    return parents, children


# ─── Strategy 3: Structure-Aware Chunking ────────────────


def chunk_structure_aware(text: str, metadata: dict | None = None) -> list[Chunk]:
    """
    Parse markdown headers → chunk theo logical structure.
    Giữ nguyên tables, code blocks, lists — không cắt giữa chừng.

    Args:
        text: Markdown text.
        metadata: Metadata gắn vào mỗi chunk.

    Returns:
        List of Chunk objects, mỗi chunk = 1 section (header + content).
    """
    metadata = metadata or {}
    sections = re.split(r"(^#{1,3}\s+.+$)", text, flags=re.MULTILINE)
    chunks: list[Chunk] = []

    current_header = ""
    current_content = ""
    for part in sections:
        if re.match(r"^#{1,3}\s+", part):
            if current_content.strip():
                header = current_header.strip() if current_header.strip() else "Preamble"
                chunks.append(Chunk(
                    text=f"{header}\n{current_content}".strip(),
                    metadata={**metadata, "section": header, "strategy": "structure", "chunk_index": len(chunks)},
                ))
            current_header = part.strip()
            current_content = ""
        else:
            current_content += part

    if current_content.strip():
        header = current_header.strip() if current_header.strip() else "Preamble"
        chunks.append(Chunk(
            text=f"{header}\n{current_content}".strip(),
            metadata={**metadata, "section": header, "strategy": "structure", "chunk_index": len(chunks)},
        ))

    return chunks


# ─── A/B Test: Compare All Strategies ────────────────────


def compare_strategies(documents: list[dict]) -> dict:
    """
    Run all strategies on documents and compare.

    Returns:
        {"basic": {...}, "semantic": {...}, "hierarchical": {...}, "structure": {...}}
    """
    def update_stats(stats: dict, chunks: list[Chunk]) -> None:
        lengths = [len(c.text) for c in chunks]
        if not lengths:
            return
        stats["count"] += len(lengths)
        stats["total_len"] += sum(lengths)
        stats["min_len"] = min(stats["min_len"], min(lengths))
        stats["max_len"] = max(stats["max_len"], max(lengths))

    results = {
        "basic": {"count": 0, "total_len": 0, "min_len": float("inf"), "max_len": 0},
        "semantic": {"count": 0, "total_len": 0, "min_len": float("inf"), "max_len": 0},
        "structure": {"count": 0, "total_len": 0, "min_len": float("inf"), "max_len": 0},
        "hierarchical": {
            "parents": {"count": 0, "total_len": 0, "min_len": float("inf"), "max_len": 0},
            "children": {"count": 0, "total_len": 0, "min_len": float("inf"), "max_len": 0},
        },
    }

    for doc in documents:
        base_chunks = chunk_basic(doc["text"], metadata=doc.get("metadata"))
        sem_chunks = chunk_semantic(doc["text"], metadata=doc.get("metadata"))
        parents, children = chunk_hierarchical(doc["text"], metadata=doc.get("metadata"))
        struct_chunks = chunk_structure_aware(doc["text"], metadata=doc.get("metadata"))

        update_stats(results["basic"], base_chunks)
        update_stats(results["semantic"], sem_chunks)
        update_stats(results["structure"], struct_chunks)
        update_stats(results["hierarchical"]["parents"], parents)
        update_stats(results["hierarchical"]["children"], children)

    def finalize(stats: dict) -> dict:
        if stats["count"] == 0:
            return {"num_chunks": 0, "avg_length": 0, "min_length": 0, "max_length": 0}
        return {
            "num_chunks": stats["count"],
            "avg_length": int(stats["total_len"] / stats["count"]),
            "min_length": int(stats["min_len"]),
            "max_length": int(stats["max_len"]),
        }

    summary = {
        "basic": finalize(results["basic"]),
        "semantic": finalize(results["semantic"]),
        "structure": finalize(results["structure"]),
        "hierarchical": {
            "parents": finalize(results["hierarchical"]["parents"]),
            "children": finalize(results["hierarchical"]["children"]),
        },
    }

    return summary


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    results = compare_strategies(docs)
    for name, stats in results.items():
        print(f"  {name}: {stats}")

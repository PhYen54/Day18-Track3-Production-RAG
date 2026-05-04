"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json, re
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation."""
    per_question: list[EvalResult] = []
    faithfulness_scores: list[float] = []
    answer_relevancy_scores: list[float] = []
    context_precision_scores: list[float] = []
    context_recall_scores: list[float] = []

    def tokenize(text: str) -> set[str]:
        return {t for t in re.findall(r"\w+", text.lower()) if t}

    def overlap_ratio(source: str, target: str) -> float:
        source_tokens = tokenize(source)
        target_tokens = tokenize(target)
        if not source_tokens or not target_tokens:
            return 0.0
        return len(source_tokens & target_tokens) / len(source_tokens)

    for question, answer, context_list, ground_truth in zip(questions, answers, contexts, ground_truths):
        # Proxy metrics with token overlap (less brittle than exact string match).
        combined_context = "\n".join(context_list)
        faithfulness = overlap_ratio(ground_truth, answer) if ground_truth else 0.0
        answer_relevancy = overlap_ratio(question, answer) if answer else 0.0
        context_precision = 1.0 if context_list else 0.0
        context_recall = overlap_ratio(ground_truth, combined_context) if ground_truth else 0.0

        faithfulness_scores.append(faithfulness)
        answer_relevancy_scores.append(answer_relevancy)
        context_precision_scores.append(context_precision)
        context_recall_scores.append(context_recall)

        per_question.append(EvalResult(
            question=question,
            answer=answer,
            contexts=context_list,
            ground_truth=ground_truth,
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=context_recall,
        ))

    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    return {
        "faithfulness": mean(faithfulness_scores),
        "answer_relevancy": mean(answer_relevancy_scores),
        "context_precision": mean(context_precision_scores),
        "context_recall": mean(context_recall_scores),
        "per_question": per_question,
    }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    def avg_score(result: EvalResult) -> float:
        return (result.faithfulness + result.answer_relevancy +
                result.context_precision + result.context_recall) / 4.0

    sorted_results = sorted(eval_results, key=avg_score)[:bottom_n]

    failures: list[dict] = []
    for result in sorted_results:
        metric_values = {
            "faithfulness": result.faithfulness,
            "answer_relevancy": result.answer_relevancy,
            "context_precision": result.context_precision,
            "context_recall": result.context_recall,
        }
        worst_metric = min(metric_values, key=metric_values.get)
        score = metric_values[worst_metric]

        if worst_metric == "faithfulness" and score < 0.85:
            diagnosis = "LLM hallucinating"
            suggested_fix = "Tighten prompt, lower temperature"
        elif worst_metric == "context_recall" and score < 0.75:
            diagnosis = "Missing relevant chunks"
            suggested_fix = "Improve chunking or add BM25"
        elif worst_metric == "context_precision" and score < 0.75:
            diagnosis = "Too many irrelevant chunks"
            suggested_fix = "Add reranking or metadata filter"
        elif worst_metric == "answer_relevancy" and score < 0.80:
            diagnosis = "Answer doesn't match question"
            suggested_fix = "Improve prompt template"
        else:
            diagnosis = "Needs review"
            suggested_fix = "Inspect the result and adjust the retrieval or prompt strategy"

        failures.append({
            "question": result.question,
            "worst_metric": worst_metric,
            "score": float(score),
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    return failures


def save_report(results: dict, failures: list[dict], path: str = "ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")


from pathlib import Path
import json
import sys

# 1. Find the project root (Code directory)
ROOT = Path(__file__).resolve().parents[1]

# 2. Add it to Python's import path BEFORE importing app
sys.path.insert(0, str(ROOT))

# 3. Import after setting the path
from app.services.processor import ProjectProcessor

# 4. Load evaluation dataset
qs = json.loads(
    (Path(__file__).resolve().parent / "evaluation_dataset.json").read_text(
        encoding="utf-8"
    )
)

p = ProjectProcessor()
stats = p.ingest_all(ROOT / "data" / "documents")

rows = []

for q in qs:
    result = p.rag.query(q["question"], top_k=5)
    answer = result["answer"].lower()
    expected = q["expected_answer"].lower()

    source_hit = any(
        s.split(":")[0].lower() == citation["filename"].lower()
        and int(s.split(":")[1]) == citation["page"]
        for s in q["expected_sources"]
        for citation in result["citations"]
    )

    keywords = [
        token for token in expected.replace(",", " ").split()
        if len(token) > 3
    ][:6]
    keyword_hit = all(token in answer for token in keywords)

    rows.append({
        "id": q["id"],
        "category": q["category"],
        "keyword_correct": keyword_hit,
        "citation_source_hit": source_hit,
        "mode": result["mode"],
        "answer": result["answer"],
        "citations": result["citations"]
    })

metrics = {
    "test_set_size": len(rows),
    "retrieval_hit_rate": round(
        sum(row["citation_source_hit"] for row in rows) / len(rows), 4
    ) if rows else 0,
    "answer_keyword_correctness": round(
        sum(row["keyword_correct"] for row in rows) / len(rows), 4
    ) if rows else 0,
    "citation_coverage": round(
        sum(bool(row["citations"]) for row in rows) / len(rows), 4
    ) if rows else 0,
    "citation_correctness": round(
        sum(row["citation_source_hit"] for row in rows) / len(rows), 4
    ) if rows else 0,
    "ingestion": stats,
    "method": (
        "Deterministic academic evaluation: expected concepts/keywords "
        "and source page matching. LLM generation was not required for "
        "the benchmark; when Ollama is unavailable, DEMO/FALLBACK mode is used."
    )
}

evaluation_dir = Path(__file__).resolve().parent

(evaluation_dir / "evaluation_metrics.json").write_text(
    json.dumps(metrics, indent=2), encoding="utf-8"
)
(evaluation_dir / "sample_outputs.json").write_text(
    json.dumps(rows[:10], indent=2), encoding="utf-8"
)

report = [
    "# Evaluation Report",
    "",
    f"Test set size: {len(rows)}",
    "",
    "## Metrics"
]

for key, value in metrics.items():
    report.append(f"- **{key}**: {value}")

report += [
    "",
    "## Interpretation",
    "This evaluation is reproducible and based on the synthetic project "
    "ground truth. It measures retrieval/source matching and deterministic "
    "concept correctness. It does not claim human or production-level quality."
]

(evaluation_dir / "evaluation_report.md").write_text(
    "\n".join(report), encoding="utf-8"
)

print(json.dumps(metrics, indent=2), flush=True)

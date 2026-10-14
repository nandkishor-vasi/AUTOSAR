# Evaluation Report

Test set size: 30

## Metrics
- **test_set_size**: 30
- **retrieval_hit_rate**: 0.9
- **answer_keyword_correctness**: 0.9
- **citation_coverage**: 1.0
- **citation_correctness**: 0.9
- **ingestion**: {'pages': 28, 'chunks': 28, 'entities': 88, 'relationships': 83}
- **method**: Deterministic academic evaluation: expected concepts/keywords and source page matching. LLM generation was not required for the benchmark; when Ollama is unavailable, DEMO/FALLBACK mode is used.

## Interpretation
This evaluation is reproducible and based on the synthetic project ground truth. It measures retrieval/source matching and deterministic concept correctness. It does not claim human or production-level quality.
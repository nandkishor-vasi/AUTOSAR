import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.processor import ProjectProcessor
p=ProjectProcessor(); print('INGEST',p.ingest_all(Path('data/documents')))
print('Ready. Run: python evaluation/run_evaluation.py')

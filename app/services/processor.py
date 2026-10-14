from pathlib import Path
from app.ingestion.pdf_loader import extract_pdf, extract_text_file
from app.ingestion.chunker import chunk_pages
from app.extraction.entities import extract_entities, relationships_from_text
from app.services.rag_service import RAGService
from app.services.db import record_document, init_db

class ProjectProcessor:
    def __init__(self):
        self.rag=RAGService()
        init_db()
        self.chunks=[]; self.entities=[]; self.relationships=[]
    def ingest_all(self, directory):
        pages=[]
        for p in sorted(Path(directory).glob('*')):
            if p.suffix.lower()=='.pdf': pages.extend(extract_pdf(p))
            elif p.suffix.lower()=='.txt': pages.extend(extract_text_file(p))
        self.chunks=chunk_pages(pages)
        self.entities=extract_entities(self.chunks)
        self.relationships=relationships_from_text(self.chunks,self.entities)
        self.rag.build(self.chunks)
        from collections import defaultdict
        page_counts=defaultdict(set)
        for p in pages: page_counts[p.filename].add(p.page_number)
        for fname, pg in page_counts.items(): record_document(fname, 'v2' if 'v2' in fname else 'v1', len(pg))
        return {'pages':len(pages),'chunks':len(self.chunks),'entities':len(self.entities),'relationships':len(self.relationships)}

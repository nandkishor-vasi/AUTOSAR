from pathlib import Path
from app.config import OLLAMA_BASE_URL, LLM_MODEL, DEMO_MODE, TOP_K
from app.rag.ollama_client import ollama_available, generate
from app.rag.retriever import Retriever
from app.services.db import record_query

class RAGService:
    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        self.retriever = Retriever(PROJECT_ROOT / "vectorstore")
    def build(self, chunks):
        self.retriever.build(chunks)

    def query(self, question, top_k=None):
        k=top_k or TOP_K
        results=self.retriever.search(question,k)
        if not results:
            return {'answer':'Insufficient evidence in the indexed project documents.','citations':[],'mode':'NO_DATA','retrieved':[]}
        context='\n\n'.join([f"SOURCE: {r['filename']} PAGE {r['page_number']}\n{r['text']}" for r in results])
        prompt=("You are an automotive architecture analysis assistant.\n"
                 "Use ONLY the provided project evidence. Do not invent facts or page numbers.\n"
                 "Answer concisely and cite sources in [Source: filename, Page N] format.\n\n"
                 f"CONTEXT:\n{context}\n\nQUESTION:\n{question}")
        full=not DEMO_MODE and ollama_available(OLLAMA_BASE_URL,LLM_MODEL)
        if full:
            try:
                answer=generate(OLLAMA_BASE_URL,LLM_MODEL,prompt)
                mode='OLLAMA'
            except Exception:
                answer=self._fallback(question,results); mode='DEMO/FALLBACK'
        else:
            answer=self._fallback(question,results); mode='DEMO/FALLBACK'
        citations=[{'filename':r['filename'],'page':r['page_number'],'section':r['section'],'score':r['score'],'excerpt':r['text'][:500]} for r in results]
        record_query(question, mode)
        return {'answer':answer,'citations':citations,'mode':mode,'retrieved':citations,'retrieval_mode':self.retriever.mode}

    def _fallback(self, question, results):
        q=question.lower()
        joined=' '.join(r['text'] for r in results)
        sentences=[]
        for r in results[:3]:
            text=r['text'].replace('\n',' ')
            if any(term in text.lower() for term in q.split() if len(term)>3):
                sentences.append(f"{text[:360]} [Source: {r['filename']}, Page {r['page_number']}]")
        if not sentences:
            sentences=[f"Relevant evidence: {r['text'][:320]} [Source: {r['filename']}, Page {r['page_number']}]" for r in results[:2]]
        return '\n'.join(sentences)

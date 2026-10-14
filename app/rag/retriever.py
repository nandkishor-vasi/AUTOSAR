from pathlib import Path
from importlib import import_module
from importlib.util import find_spec
import json
import numpy as np

try:
    TfidfVectorizer = import_module('sklearn.feature_extraction.text').TfidfVectorizer
except Exception:
    TfidfVectorizer = None

try:
    chromadb = import_module('chromadb') if find_spec('chromadb') is not None else None
except Exception:
    chromadb = None

try:
    SentenceTransformer = import_module('sentence_transformers').SentenceTransformer
except Exception:
    SentenceTransformer = None

class Retriever:
    def __init__(self, persist_path: Path):
        self.persist_path=Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.docs=[]
        self.vectorizer=None
        self.matrix=None
        self.embedding_model=None
        self.collection=None
        self.mode='fallback-tfidf'
        self._load()

    def _load(self):
        f=self.persist_path/'chunks.json'
        if f.exists():
            self.docs=json.loads(f.read_text(encoding='utf-8'))
        # Semantic dependencies are optional; never block demo mode.
        if chromadb is not None and SentenceTransformer is not None and self.docs:
            try:
                self.embedding_model=SentenceTransformer('all-MiniLM-L6-v2')
                client=chromadb.PersistentClient(path=str(self.persist_path/'chroma_db'))
                self.collection=client.get_or_create_collection('autosar_hld')
                self.mode='sentence-transformers + ChromaDB'
            except Exception:
                self.embedding_model=None; self.collection=None
        if self.docs:
            texts=[d['text'] for d in self.docs]
            self.vectorizer=TfidfVectorizer(stop_words='english')
            self.matrix=self.vectorizer.fit_transform(texts)

    def build(self, chunks):
        self.docs=[c.__dict__ for c in chunks]
        (self.persist_path/'chunks.json').write_text(json.dumps(self.docs,indent=2),encoding='utf-8')
        texts=[d['text'] for d in self.docs]
        self.vectorizer=TfidfVectorizer(stop_words='english')
        self.matrix=self.vectorizer.fit_transform(texts) if texts else None
        self.mode='fallback-tfidf'
        if chromadb is not None and SentenceTransformer is not None and texts:
            try:
                self.embedding_model=SentenceTransformer('all-MiniLM-L6-v2')
                client=chromadb.PersistentClient(path=str(self.persist_path/'chroma_db'))
                self.collection=client.get_or_create_collection('autosar_hld')
                ids=[d['chunk_id'] for d in self.docs]
                embeddings=self.embedding_model.encode(texts, normalize_embeddings=True).tolist()
                self.collection.upsert(ids=ids,documents=texts,embeddings=embeddings,metadatas=[{k:str(d[k]) for k in ['filename','page_number','section','document_version']} for d in self.docs])
                self.mode='sentence-transformers + ChromaDB'
            except Exception:
                self.embedding_model=None; self.collection=None

    def search(self, query, k=5):
        if self.collection is not None and self.embedding_model is not None:
            try:
                q=self.embedding_model.encode([query], normalize_embeddings=True).tolist()
                result=self.collection.query(query_embeddings=q,n_results=min(k,len(self.docs)),include=['documents','metadatas','distances'])
                out=[]
                id_map={d['chunk_id']:d for d in self.docs}
                ids=result.get('ids',[[]])[0]
                docs=result.get('documents',[[]])[0]
                metas=result.get('metadatas',[[]])[0]
                dists=result.get('distances',[[]])[0]
                for cid,txt,meta,dist in zip(ids,docs,metas,dists):
                    base=id_map.get(cid,{})
                    out.append({**base,'text':txt,'score':float(1.0/(1.0+dist))})
                return out
            except Exception:
                pass
        if not self.docs or self.matrix is None: return []
        q=self.vectorizer.transform([query])
        scores=(self.matrix @ q.T).toarray().ravel()
        idx=np.argsort(-scores)[:k]
        return [{**self.docs[i], 'score': float(scores[i])} for i in idx]

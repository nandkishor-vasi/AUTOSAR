from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from app.config import DOCS_DIR
from app.models.schemas import QueryRequest, CompareRequest, ImpactRequest
from app.services.processor import ProjectProcessor
from app.impact.analysis import impact_analysis

router=APIRouter()
processor=ProjectProcessor()

@router.get('/health')
def health(): return {'status':'ok','service':'autosar-hld-ai'}

@router.post('/documents/upload')
async def upload(file: UploadFile=File(...)):
    if file.filename is None or Path(file.filename).suffix.lower() not in {'.pdf','.txt'}: raise HTTPException(400,'Only PDF/TXT supported')
    name=Path(file.filename).name
    dest=DOCS_DIR/name
    with dest.open('wb') as f: shutil.copyfileobj(file.file,f)
    return {'filename':name,'status':'uploaded'}

@router.post('/documents/ingest')
def ingest(): return processor.ingest_all(DOCS_DIR)

@router.get('/documents')
def documents(): return [{'filename':p.name} for p in sorted(DOCS_DIR.glob('*')) if p.is_file()]

@router.post('/query')
def query(req: QueryRequest): return processor.rag.query(req.question,req.top_k)

@router.get('/entities/{entity_name}')
def entity(entity_name: str):
    return {'entity':entity_name,'matches':[e for e in processor.entities if e['name'].lower()==entity_name.lower()]}

@router.post('/impact-analysis')
def impact(req: ImpactRequest): return impact_analysis(req.entity_name,processor.relationships)

@router.post('/compare')
def compare(req: CompareRequest):
    from app.ingestion.pdf_loader import extract_pdf
    from app.ingestion.chunker import chunk_pages
    from app.comparison.compare import compare_entity_sets
    old=DOCS_DIR/req.old_document; new=DOCS_DIR/req.new_document
    if not old.exists() or not new.exists(): raise HTTPException(404,'Document not found')
    return compare_entity_sets(chunk_pages(extract_pdf(old)),chunk_pages(extract_pdf(new)))

@router.post('/inconsistencies')
def inconsistencies():
    findings=[]
    names={e['name'] for e in processor.entities}
    for r in processor.relationships:
        if r['relation']=='depends_on' and r['target'] not in names:
            findings.append({'type':'missing_dependency_target','severity':'medium','status':'POTENTIAL INCONSISTENCY','evidence':r['evidence'],'source':r['document'],'page':r['page']})
    # intentional v2 legacy interface conflict
    refs=[e for e in processor.entities if e['type']=='interface']
    has_old=any(e['name']=='EngineSpeedInterface' and 'v2' in e['document'] for e in refs)
    has_new=any(e['name']=='PowertrainSpeedInterface' and 'v2' in e['document'] for e in refs)
    if has_old and has_new:
        findings.append({'type':'interface_name_conflict','severity':'high','status':'POTENTIAL INCONSISTENCY','evidence':'v2 contains both legacy and revised interface terminology.','source':'vehicle_control_hld_v2.pdf','page':6})
    return {'count':len(findings),'findings':findings}

@router.get('/evaluation/results')
def evaluation_results():
    p=Path('evaluation/evaluation_metrics.json')
    return __import__('json').loads(p.read_text()) if p.exists() else {'status':'not_run'}

@router.get('/system/info')
def system_info():
    import platform
    from app.config import APP_VERSION,LLM_MODEL,EMBEDDING_MODEL,DEMO_MODE
    return {'app_version':APP_VERSION,'python':platform.python_version(),'llm_model':LLM_MODEL,'embedding_model':EMBEDDING_MODEL,'vector_db':'ChromaDB (optional) / TF-IDF fallback','mode':'DEMO/FALLBACK' if DEMO_MODE else 'LLM auto-detect'}

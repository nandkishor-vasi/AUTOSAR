import streamlit as st
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.services.processor import ProjectProcessor
from app.impact.analysis import impact_analysis

st.set_page_config(page_title='AUTOSAR InsightAI',page_icon='🚗',layout='wide')
@st.cache_resource
def get_processor():
    p=ProjectProcessor(); p.ingest_all(Path(__file__).resolve().parents[1]/'data/documents'); return p

p=get_processor()
st.title('AUTOSAR InsightAI')
st.caption('Synthetic academic project - Architecture Intelligence & Impact Analysis')
menu=st.sidebar.radio('Navigation',['Dashboard','Documents','Ask the HLD','Architecture Explorer','Impact Analysis','Compare Revisions','Inconsistency Analysis','Evaluation','System Information'])

if menu=='Dashboard':
    c=p.ingest_all(Path(__file__).resolve().parents[1]/'data/documents')
    cols=st.columns(6)
    for col,(k,v) in zip(cols,c.items()): col.metric(k.title(),v)
    st.info('All documents are synthetic and intended only for academic demonstration.')
elif menu=='Documents':
    st.subheader('Knowledge Base Documents')
    for d in sorted((Path(__file__).resolve().parents[1]/'data/documents').glob('*')): st.write(d.name)
elif menu=='Ask the HLD':
    q=st.text_input('Ask an architecture question')
    if st.button('Ask') and q:
        with st.spinner("Retrieving relevant HLD evidence and generating answer..."):
            r=p.rag.query(q); st.markdown(r['answer']); st.caption('Mode: '+r['mode'])
        for s in r['citations']:
            with st.expander(f"{s['filename']} - Page {s['page']}"):
                st.write(s['excerpt'])
elif menu=='Architecture Explorer':
    names=sorted({e['name'] for e in p.entities})
    ent=st.selectbox('Select entity',names) if names else None
    if ent:
        st.write([e for e in p.entities if e['name']==ent])
        st.write([r for r in p.relationships if r['source']==ent or r['target']==ent])
elif menu=='Impact Analysis':
    names=sorted({e['name'] for e in p.entities})
    ent=st.selectbox('Entity',names)
    if st.button('Analyze Impact'):
        result=impact_analysis(ent,p.relationships)
        st.json(result)
elif menu=='Compare Revisions':
    from app.ingestion.pdf_loader import extract_pdf
    from app.ingestion.chunker import chunk_pages
    from app.comparison.compare import compare_entity_sets
    a=Path(__file__).resolve().parents[1]/'data/documents/vehicle_control_hld_v1.pdf'; b=Path(__file__).resolve().parents[1]/'data/documents/vehicle_control_hld_v2.pdf'
    if st.button('Compare v1 vs v2'):
        st.json(compare_entity_sets(chunk_pages(extract_pdf(a)),chunk_pages(extract_pdf(b))))
elif menu=='Inconsistency Analysis':
    if st.button('Analyze'):
        names={e['name'] for e in p.entities}; findings=[]
        if any(e['name']=='EngineSpeedInterface' and 'v2' in e['document'] for e in p.entities) and any(e['name']=='PowertrainSpeedInterface' and 'v2' in e['document'] for e in p.entities):
            findings.append({'status':'POTENTIAL INCONSISTENCY','severity':'high','finding':'Legacy EngineSpeedInterface and revised PowertrainSpeedInterface both appear in v2.'})
        st.json(findings)
elif menu=='Evaluation':
    f=Path(__file__).resolve().parents[2]/"evaluation_results" / "evaluation_metrics.json"
    if f.exists(): st.json(__import__('json').loads(f.read_text()))
    else: st.warning('Run evaluation_results/run_evaluation.py first.')
elif menu=='System Information':
    import platform
    from app.config import LLM_MODEL, OLLAMA_BASE_URL, DEMO_MODE

    st.json({
        'python': platform.python_version(),
        'llm_provider': 'Ollama',
        'llm_model': LLM_MODEL,
        'ollama_url': OLLAMA_BASE_URL,
        'embedding': 'all-MiniLM-L6-v2',
        'vector_store': 'ChromaDB',
        'retrieval': 'Semantic retrieval',
        'demo_mode': DEMO_MODE
    })
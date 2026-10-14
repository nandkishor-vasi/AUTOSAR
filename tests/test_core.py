from pathlib import Path
from app.ingestion.pdf_loader import extract_pdf
from app.ingestion.chunker import chunk_pages
from app.extraction.entities import extract_entities, relationships_from_text
from app.impact.analysis import impact_analysis

def test_pdf_and_chunks():
    pages=extract_pdf(Path('data/documents/vehicle_control_hld_v1.pdf'))
    assert len(pages)>=9
    chunks=chunk_pages(pages)
    assert len(chunks)>0
    assert all(c.page_number>=1 for c in chunks)

def test_entities_and_relationships():
    pages=extract_pdf(Path('data/documents/vehicle_control_hld_v1.pdf'))
    chunks=chunk_pages(pages)
    ents=extract_entities(chunks)
    names={e['name'] for e in ents}
    assert 'EngineControlSWC' in names
    assert 'EngineSpeedInterface' in names
    rel=relationships_from_text(chunks,ents)
    assert any(r['relation']=='uses_or_provides' for r in rel)

def test_impact():
    rel=[{'source':'VehicleControlSWC','relation':'depends_on','target':'EngineControlSWC','document':'x','page':1,'evidence':'e','confidence':'source'}]
    x=impact_analysis('VehicleControlSWC',rel)
    assert 'EngineControlSWC' in x['related_entities']

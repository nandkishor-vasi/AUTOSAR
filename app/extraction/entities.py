import re
from collections import defaultdict

PATTERNS={
'component':r'\b(?:[A-Z][A-Za-z0-9]+SWC|[A-Z][A-Za-z0-9]+Gateway|[A-Z][A-Za-z0-9]+ECU)\b',
'interface':r'\b[A-Z][A-Za-z0-9]+Interface\b',
'port':r'\b[PR]_[A-Za-z0-9]+\b',
'signal':r'\b(?:EngineSpeedStatus|EngineSpeed|VehicleSpeed|VehicleCommand|EngineCommand)\b',
'runnable':r'\b[A-Z][A-Za-z0-9]+\b(?=\s+runnable|\s+contains runnable)',
}

def extract_entities(chunks):
    entities=[]; seen=set()
    for c in chunks:
        for typ,pat in PATTERNS.items():
            for m in re.findall(pat,c.text):
                key=(typ,m,c.filename,c.page_number)
                if key in seen: continue
                seen.add(key)
                entities.append({'type':typ,'name':m,'document':c.filename,'page':c.page_number,'chunk_id':c.chunk_id,'method':'regex'})
    return entities

def relationships_from_text(chunks, entities):
    names_by_type=defaultdict(set)
    for e in entities: names_by_type[e['type']].add(e['name'])
    rel=[]
    for c in chunks:
        text=c.text
        comps=[n for n in names_by_type['component'] if n in text]
        interfaces=[n for n in names_by_type['interface'] if n in text]
        ports=[n for n in names_by_type['port'] if n in text]
        signals=[n for n in names_by_type['signal'] if n in text]
        for comp in comps:
            for intf in interfaces: rel.append({'source':comp,'relation':'uses_or_provides','target':intf,'document':c.filename,'page':c.page_number,'evidence':text[:350],'confidence':'source'})
            for port in ports: rel.append({'source':comp,'relation':'has_port','target':port,'document':c.filename,'page':c.page_number,'evidence':text[:350],'confidence':'source'})
            for other in comps:
                if other!=comp and re.search(rf'{re.escape(comp)}.{0,120}depends on.{0,120}{re.escape(other)}',text,re.I|re.S):
                    rel.append({'source':comp,'relation':'depends_on','target':other,'document':c.filename,'page':c.page_number,'evidence':text[:350],'confidence':'source'})
        for intf in interfaces:
            for sig in signals:
                if sig.lower() in text.lower(): rel.append({'source':intf,'relation':'carries','target':sig,'document':c.filename,'page':c.page_number,'evidence':text[:350],'confidence':'source'})
    # dedupe
    out=[]; seen=set()
    for r in rel:
        k=(r['source'],r['relation'],r['target'],r['document'],r['page'])
        if k not in seen: seen.add(k); out.append(r)
    return out

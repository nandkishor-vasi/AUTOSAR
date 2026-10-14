def impact_analysis(entity_name, relationships):
    incoming=[]; outgoing=[]
    for r in relationships:
        if r['source']==entity_name: outgoing.append(r)
        if r['target']==entity_name: incoming.append(r)
    confirmed=outgoing+incoming
    related=[]
    for r in confirmed:
        related.append(r['target'] if r['source']==entity_name else r['source'])
    return {'entity':entity_name,'confirmed_relationships':confirmed,'related_entities':sorted(set(related)),'inferred_impacts':[], 'note':'Potential impact is inferred only when no direct confirmed relationship exists.'}

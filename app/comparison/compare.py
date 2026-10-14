from app.extraction.entities import extract_entities, relationships_from_text

def compare_entity_sets(old_chunks,new_chunks):
    old=extract_entities(old_chunks); new=extract_entities(new_chunks)
    oldset={(e['type'],e['name']) for e in old}; newset={(e['type'],e['name']) for e in new}
    return {
        'added':[{'type':t,'name':n} for t,n in sorted(newset-oldset)],
        'removed':[{'type':t,'name':n} for t,n in sorted(oldset-newset)],
        'common_count':len(oldset&newset)
    }

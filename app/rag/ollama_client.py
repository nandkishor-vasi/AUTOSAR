import requests
from .retriever import Retriever

def ollama_available(base_url, model):
    try:
        r=requests.get(base_url.rstrip('/')+'/api/tags',timeout=2)
        if r.status_code!=200: return False
        names=[m.get('name','') for m in r.json().get('models',[])]
        return any(n==model or n.startswith(model) for n in names)
    except Exception:
        return False

def generate(base_url, model, prompt, temperature=0.1):
    r=requests.post(base_url.rstrip('/')+'/api/generate',json={'model':model,'prompt':prompt,'stream':False,'options':{'temperature':temperature}},timeout=60)
    r.raise_for_status()
    return r.json().get('response','').strip()

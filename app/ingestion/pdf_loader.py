from pathlib import Path
import fitz
from dataclasses import dataclass, asdict
import re

@dataclass
class PageRecord:
    document_id: str
    filename: str
    page_number: int
    text: str
    section: str
    version: str

def infer_version(name: str) -> str:
    m = re.search(r"_(v\d+)", name.lower())
    return m.group(1) if m else "v1"

def extract_pdf(path: Path):
    doc = fitz.open(path)
    records=[]
    current_section="General"
    for idx,page in enumerate(doc):
        text=page.get_text("text") or ""
        lines=[x.strip() for x in text.splitlines() if x.strip()]
        if lines and len(lines[0])<80 and not lines[0].startswith("SYNTHETIC DATA"):
            current_section=lines[0]
        records.append(PageRecord(
            document_id=path.stem, filename=path.name, page_number=idx+1,
            text=text.strip(), section=current_section, version=infer_version(path.name)))
    return records

def extract_text_file(path: Path):
    text=path.read_text(encoding="utf-8", errors="ignore")
    return [PageRecord(path.stem,path.name,1,text,"General",infer_version(path.name))]

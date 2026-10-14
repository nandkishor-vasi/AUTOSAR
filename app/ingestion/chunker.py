from dataclasses import dataclass, asdict
import re

@dataclass
class Chunk:
    document_id: str
    filename: str
    page_number: int
    section: str
    chunk_id: str
    source_type: str
    document_version: str
    text: str

# def chunk_pages(pages, chunk_size=900, overlap=120):
#     out=[]
#     for p in pages:
#         text=p.text.strip()
#         if not text: continue
#         paragraphs=[x.strip() for x in re.split(r"\n\s*\n", text) if x.strip()]
#         if not paragraphs: paragraphs=[text]
#         current=""
#         counter=0
#         for para in paragraphs:
#             if current and len(current)+len(para)+1 > chunk_size:
#                 out.append(Chunk(p.document_id,p.filename,p.page_number,p.section,f"{p.document_id}_c{counter}","pdf",p.version,current.strip()))
#                 counter += 1
#                 tail=current[-overlap:] if overlap else ""
#                 current=tail+" "+para
#             else:
#                 current=(current+" "+para).strip()
#         if current:
#             out.append(Chunk(p.document_id,p.filename,p.page_number,p.section,f"{p.document_id}_c{counter}","pdf",p.version,current.strip()))
#     return out
def chunk_pages(pages, chunk_size=900, overlap=120):
    out = []

    for p in pages:
        text = p.text.strip()
        if not text:
            continue

        paragraphs = [
            x.strip()
            for x in re.split(r"\n\s*\n", text)
            if x.strip()
        ]

        if not paragraphs:
            paragraphs = [text]

        current = ""
        counter = 0

        for para in paragraphs:
            if current and len(current) + len(para) + 1 > chunk_size:

                chunk_id = (
                    f"{p.document_id}"
                    f"_p{p.page_number}"
                    f"_c{counter}"
                )

                out.append(
                    Chunk(
                        p.document_id,
                        p.filename,
                        p.page_number,
                        p.section,
                        chunk_id,
                        "pdf",
                        p.version,
                        current.strip()
                    )
                )

                counter += 1

                tail = current[-overlap:] if overlap else ""
                current = tail + " " + para

            else:
                current = (current + " " + para).strip()

        if current:
            chunk_id = (
                f"{p.document_id}"
                f"_p{p.page_number}"
                f"_c{counter}"
            )

            out.append(
                Chunk(
                    p.document_id,
                    p.filename,
                    p.page_number,
                    p.section,
                    chunk_id,
                    "pdf",
                    p.version,
                    current.strip()
                )
            )

    return out
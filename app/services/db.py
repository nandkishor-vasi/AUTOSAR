from pathlib import Path
import sqlite3
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "project.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    con=sqlite3.connect(DB_PATH)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS documents (filename TEXT PRIMARY KEY, version TEXT, pages INTEGER, ingested_at TEXT);
    CREATE TABLE IF NOT EXISTS query_log (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, mode TEXT, created_at TEXT);
    """)
    con.commit(); con.close()

def record_document(filename, version, pages):
    init_db(); con=sqlite3.connect(DB_PATH); con.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?)",(filename,version,pages,datetime.now().isoformat())); con.commit(); con.close()

def record_query(question, mode):
    init_db(); con=sqlite3.connect(DB_PATH); con.execute("INSERT INTO query_log(question,mode,created_at) VALUES (?,?,?)",(question,mode,datetime.now().isoformat())); con.commit(); con.close()


import sqlite3
from pathlib import Path
import sqlite_vec


def connect(path: Path| str=":memory:") -> sqlite3.Connection:
    conn= sqlite3.connect(path)
    conn.row_factory= sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

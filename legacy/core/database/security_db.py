import sqlite3
from pathlib import Path


DB=Path.home()/\
"STARCORE/core/database/starcore.db"


def init():

    conn=sqlite3.connect(DB)

    cur=conn.cursor()


    tables={


    "security_snapshots":
    """
    CREATE TABLE IF NOT EXISTS security_snapshots(
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    category TEXT,
    data TEXT
    )
    """,


    "integrity_checks":
    """
    CREATE TABLE IF NOT EXISTS integrity_checks(
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    check_name TEXT,
    result TEXT
    )
    """,


    "root_events":
    """
    CREATE TABLE IF NOT EXISTS root_events(
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    event TEXT,
    status TEXT
    )
    """

    }


    for sql in tables.values():
        cur.execute(sql)


    conn.commit()
    conn.close()


if __name__=="__main__":
    init()
    print("Security database ready")


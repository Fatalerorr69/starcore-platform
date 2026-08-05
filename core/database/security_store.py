import sqlite3
import json

from pathlib import Path
from datetime import datetime


DB=Path.home()/\
"STARCORE/core/database/starcore.db"



def save(category,data):

    conn=sqlite3.connect(DB)

    cur=conn.cursor()


    cur.execute(
    """
    INSERT INTO security_snapshots
    (
    timestamp,
    category,
    data
    )
    VALUES (?,?,?)
    """,
    (
        str(datetime.now()),
        category,
        json.dumps(data)
    )
    )


    conn.commit()
    conn.close()



if __name__=="__main__":

    save(
        "test",
        {
        "status":"ok"
        }
    )

    print(
        "snapshot stored"
    )


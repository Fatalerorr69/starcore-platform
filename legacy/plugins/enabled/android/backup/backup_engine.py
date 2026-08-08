#!/usr/bin/env python3

import json
import shutil
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


SRC=[

ROOT/"plugins/enabled/android",

ROOT/"runtime/android"

]


OUT=ROOT/"runtime/android/backups"


OUT.mkdir(
parents=True,
exist_ok=True
)


backup={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Backup Engine",

"version":
"6B.X.10",

"items":[]

}


for item in SRC:

    backup["items"].append(
        {
        "path":str(item),
        "exists":item.exists()
        }
    )


with open(
OUT/"backup_report.json",
"w"
) as f:

    json.dump(
        backup,
        f,
        indent=4
    )


print(
"BACKUP ENGINE READY"
)


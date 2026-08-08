#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/update"
OUT.mkdir(parents=True,exist_ok=True)


backup={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Backup Engine",
"type":"runtime_snapshot",
"status":"created"
}


json.dump(
backup,
open(OUT/"backup_history.json","w"),
indent=4
)

print("BACKUP READY")


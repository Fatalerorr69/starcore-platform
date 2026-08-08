#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/update"
OUT.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Update Manager",
"version":"6B.X.19",
"current_release":"6B.X.18",
"next_release":"6B.X.19",
"status":"ready"
}


json.dump(
data,
open(OUT/"version_registry.json","w"),
indent=4
)

print("UPDATE MANAGER READY")


#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/security"


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Security Baseline",
"policy":"standard",
"status":"active"
}


json.dump(
data,
open(OUT/"baseline.json","w"),
indent=4
)

print("BASELINE READY")


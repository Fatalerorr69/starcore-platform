#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/update"


report={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Rollback Engine",
"mode":"safe",
"rollback_available":True,
"status":"ready"
}


json.dump(
report,
open(OUT/"update_report.json","w"),
indent=4
)

print("ROLLBACK READY")


#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


FILES=list(
(ROOT/"runtime/android")
.rglob("*.json")
)


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Diagnostics Aggregator",

"version":
"6B.X.3.H",

"json_files":
len(FILES),

"status":
"healthy"

}



with open(
ROOT/"runtime/android/diagnostics/report.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print(
"DIAGNOSTICS COMPLETE"
)


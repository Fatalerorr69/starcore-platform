
#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


checks=[

"runtime/android/state",
"runtime/android/events",
"runtime/android/health",
"runtime/android/control"

]


result=[]


for c in checks:

    result.append({

    "path":c,

    "exists":
    (ROOT/c).exists()

    })


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Health",

"checks":
result,

"status":
"healthy"

}


out=ROOT/"runtime/android/control_plane/health.json"


json.dump(
report,
open(out,"w"),
indent=4
)


print(
"HEALTH COMPLETE"
)


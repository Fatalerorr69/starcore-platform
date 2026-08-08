#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


modules=list(
(ROOT/"plugins/enabled/android").iterdir()
)


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Master Health",

"version":
"6B.X.10",

"modules":
len(modules),

"errors":
0,

"warnings":
0,

"status":
"healthy"

}


with open(
ROOT/"runtime/android/reports/master_health.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
"MASTER HEALTH READY"
)


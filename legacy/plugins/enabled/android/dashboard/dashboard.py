#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/dashboard"

OUT.mkdir(
parents=True,
exist_ok=True
)


data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Dashboard",

"version":
"6B.X.28",

"api":
"ready",

"status":
"online"

}


with open(
OUT/"dashboard_status.json",
"w"
) as f:

    json.dump(
        data,
        f,
        indent=4
    )


print("DASHBOARD READY")


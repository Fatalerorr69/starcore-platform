#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"


STATE = ROOT / "runtime/android/state/core_state.json"

OUT = ROOT / "runtime/android/control"


OUT.mkdir(
    parents=True,
    exist_ok=True
)



result = {

    "timestamp":
        datetime.now().isoformat(),

    "controller":
        "STARCORE Android Core Controller",

    "version":
        "6B.X.3.A",

    "actions":[],

    "status":
        "healthy"

}



if STATE.exists():

    with open(STATE) as f:

        state=json.load(f)


    result["actions"].append(
        {
            "state":
            "loaded"
        }
    )

    result["core_status"] = state["status"]


else:

    result["status"]="warning"

    result["actions"].append(
        {
            "state":
            "missing"
        }
    )



with open(
    OUT/"controller_status.json",
    "w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"CORE CONTROLLER COMPLETE"
)


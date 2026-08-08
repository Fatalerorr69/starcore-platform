#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


OUT=Path.home()/ "STARCORE/runtime/android/operations"


policy={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Operation Policy",

"version":
"6B.Y.33",

"rules":
[
"backup_before_change",
"validate_after_execution",
"keep_history"
],

"status":
"active"

}


with open(
OUT/"operation_policy.json",
"w"
) as f:

    json.dump(
        policy,
        f,
        indent=4
    )


print("POLICY MANAGER ONLINE")


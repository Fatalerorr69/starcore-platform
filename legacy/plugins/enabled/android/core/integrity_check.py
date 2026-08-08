#!/usr/bin/env python3


import json
import hashlib
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

PLUGIN=ROOT/"plugins/enabled/android"


FILES=list(
PLUGIN.rglob("*.py")
)


result={

"timestamp":
datetime.now().isoformat(),

"files":len(FILES),

"checks":[]

}



for f in FILES:

    h=hashlib.sha256(
        f.read_bytes()
    ).hexdigest()


    result["checks"].append({

    "file":
    str(f.relative_to(ROOT)),

    "sha256":
    h

    })



OUT=ROOT/"runtime/android/master/plugin_integrity.json"


OUT.parent.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT,
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"PLUGIN INTEGRITY COMPLETE"
)


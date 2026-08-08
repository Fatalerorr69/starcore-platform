#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


files=list(
(ROOT/"runtime/android").rglob("*.json")
)


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Release Manifest",

"version":
"6B.X.18",

"json_files":
len(files),

"release":
"ANDROID_INTELLIGENCE_CORE",


"status":
"production-ready"

}



OUT=ROOT/"runtime/android/release"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"release_manifest.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print(
"RELEASE MANIFEST COMPLETE"
)


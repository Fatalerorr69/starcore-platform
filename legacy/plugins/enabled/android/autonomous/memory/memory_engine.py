#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/autonomous/memory"

OUT.mkdir(parents=True,exist_ok=True)


memory={

"timestamp":datetime.now().isoformat(),

"memory_type":"persistent",

"entries":0,

"status":"initialized"

}


with open(
OUT/"memory.json",
"w"
) as f:

 json.dump(
 memory,
 f,
 indent=4
 )


print("MEMORY ENGINE READY")

#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/distributed"

OUT.mkdir(parents=True,exist_ok=True)


nodes=[

{
"name":"android-starcore",
"type":"edge",
"status":"online"
},

{
"name":"fatalab-ai-core",
"type":"compute",
"status":"unknown"
}

]


json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Node Registry",
"version":"6B.Y.7",
"nodes":nodes
},
open(OUT/"node_registry.json","w"),
indent=4
)


print("NODE DISCOVERY COMPLETE")


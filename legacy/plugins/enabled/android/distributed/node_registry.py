#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/distributed"

OUT.mkdir(parents=True,exist_ok=True)


registry={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Distributed Node Registry",

"version":
"6B.Y.2",

"nodes":

[

{

"name":"android-starcore",

"type":"edge-node",

"status":"online"

},

{

"name":"fatalab-ai-core",

"type":"compute-node",

"status":"pending"

}

],

"status":
"active"

}


with open(
OUT/"node_registry.json",
"w"
) as f:

    json.dump(
        registry,
        f,
        indent=4
    )


print("NODE REGISTRY READY")


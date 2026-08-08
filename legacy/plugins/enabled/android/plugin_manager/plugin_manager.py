#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

MODULES=ROOT/"plugins/enabled/android"

OUT=ROOT/"runtime/android/plugin_manager"

OUT.mkdir(parents=True,exist_ok=True)


plugins=[]

for p in MODULES.iterdir():

    if p.is_dir():

        plugins.append({
            "plugin":p.name,
            "enabled":True,
            "exists":True
        })


report={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE Plugin Manager",

"version":
"6B.X.26",

"plugins":
plugins,

"status":
"healthy"

}


with open(
OUT/"plugin_registry.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print("PLUGIN MANAGER COMPLETE")


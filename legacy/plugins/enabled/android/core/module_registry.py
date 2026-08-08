#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

PLUGIN_DIR = ROOT / "plugins/enabled/android"

OUT = ROOT / "runtime/android/registry"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


modules = []


for item in PLUGIN_DIR.iterdir():

    if item.is_dir():

        modules.append(
            {
                "module": item.name,
                "path": str(item.relative_to(ROOT)),
                "enabled": True
            }
        )


registry = {

    "timestamp":
        datetime.now().isoformat(),

    "core":
        "STARCORE Android Intelligence Core",

    "version":
        "6B.X.2.1",

    "modules":
        modules

}


with open(
    OUT / "module_registry.json",
    "w"
) as f:

    json.dump(
        registry,
        f,
        indent=4
    )


print("MODULE REGISTRY COMPLETE")
print(
    "Modules:",
    len(modules)
)


#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

REGISTRY = ROOT / "runtime/android/registry/module_registry.json"

OUT = ROOT / "runtime/android/runtime"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


def load_registry():

    if not REGISTRY.exists():
        return {}

    with open(REGISTRY) as f:
        return json.load(f)



def check_module(module):

    path = ROOT / module["path"]

    return {
        "module": module["module"],
        "enabled": module["enabled"],
        "exists": path.exists(),
        "path": str(path)
    }



def main():

    registry = load_registry()

    result = {

        "timestamp":
            datetime.now().isoformat(),

        "component":
            "STARCORE Android Runtime Manager",

        "modules":[]

    }


    for module in registry.get("modules", []):

        result["modules"].append(
            check_module(module)
        )


    result["healthy"] = all(
        x["exists"]
        for x in result["modules"]
    )


    output = OUT / "runtime_manager.json"


    with open(output,"w") as f:

        json.dump(
            result,
            f,
            indent=4
        )


    print(
        "RUNTIME MANAGER COMPLETE"
    )

    print(output)



if __name__=="__main__":
    main()


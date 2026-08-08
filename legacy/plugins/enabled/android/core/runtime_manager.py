#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"


REGISTRY = ROOT / "runtime/android/registry/module_registry.json"

OUT = ROOT / "runtime/android/health"


OUT.mkdir(
    parents=True,
    exist_ok=True
)


result = {

    "timestamp":
        datetime.now().isoformat(),

    "runtime":
        "STARCORE Android Runtime",

    "status":
        "healthy",

    "checks":[]

}


if REGISTRY.exists():

    result["checks"].append(
        {
            "registry":
            "available"
        }
    )

else:

    result["status"]="warning"

    result["checks"].append(
        {
            "registry":
            "missing"
        }
    )



with open(
    OUT/"runtime_status.json",
    "w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
    "RUNTIME MANAGER COMPLETE"
)


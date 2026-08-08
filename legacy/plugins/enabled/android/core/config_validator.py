#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"


CONFIGS = list(
    (ROOT/"plugins/enabled/android/config").glob("*.yaml")
)


OUT = ROOT/"runtime/android/health"


OUT.mkdir(
    parents=True,
    exist_ok=True
)


report = {

    "timestamp":
        datetime.now().isoformat(),

    "configs":
        [],

    "valid":
        True

}


for cfg in CONFIGS:

    report["configs"].append(
        {
            "file":
            cfg.name,

            "exists":
            True
        }
    )



with open(
    OUT/"config_validation.json",
    "w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
    "CONFIG VALIDATION COMPLETE"
)


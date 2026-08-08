#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

OUT = ROOT / "runtime/android/bridge"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


bridge = {

    "timestamp":
        datetime.now().isoformat(),

    "component":
        "STARCORE AI Bridge",

    "version":
        "6B.X.7.C",

    "interfaces": {

        "local_ai":
            True,

        "fatalab_bridge":
            False,

        "remote_ready":
            True
    },

    "status":
        "ready"

}


with open(
    OUT / "ai_bridge.json",
    "w"
) as f:

    json.dump(
        bridge,
        f,
        indent=4
    )


print(
    "AI BRIDGE READY"
)


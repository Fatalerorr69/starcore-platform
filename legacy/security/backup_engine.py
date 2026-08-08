#!/usr/bin/env python3

import os
import json
from datetime import datetime


BASE=os.path.expanduser("~/STARCORE")


backup={

    "component":
    "STARCORE Backup Engine",

    "version":
    "7.0.14",

    "timestamp":
    datetime.utcnow().isoformat(),

    "backup_root":
    "runtime/backups",

    "targets":[
        "runtime",
        "registry",
        "plugins",
        "config"
    ],

    "status":
    "ready"
}


with open(
f"{BASE}/runtime/backups/backup_registry.json",
"w"
) as f:
    json.dump(
        backup,
        f,
        indent=4
    )


with open(
f"{BASE}/runtime/backups/snapshot_state.json",
"w"
) as f:
    json.dump(
        {
            "snapshot":
            "STARCORE_7.0.13",
            "created":
            datetime.utcnow().isoformat(),
            "status":
            "available"
        },
        f,
        indent=4
    )


print("BACKUP ENGINE ONLINE")


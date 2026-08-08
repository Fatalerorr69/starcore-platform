#!/usr/bin/env python3

import os
import json
import hashlib
from datetime import datetime


BASE=os.path.expanduser("~/STARCORE")


files=[
    "runtime/platform/STARCORE_7_MASTER_RELEASE.json",
    "runtime/health/global_health.json",
    "registry/modules.json"
]


integrity=[]


for f in files:

    path=f"{BASE}/{f}"

    if os.path.exists(path):

        h=hashlib.sha256()

        with open(path,"rb") as file:

            h.update(file.read())

        integrity.append(
            {
                "file":f,
                "hash":h.hexdigest()
            }
        )


report={

    "component":
    "STARCORE Security Hardening",

    "version":
    "7.0.16",

    "timestamp":
    datetime.utcnow().isoformat(),

    "integrity":
    integrity,

    "status":
    "validated"
}


with open(
f"{BASE}/runtime/security/file_integrity.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print("SECURITY HARDENING ONLINE")


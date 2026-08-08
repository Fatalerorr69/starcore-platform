#!/usr/bin/env python3

import json
import os

BASE=os.path.expanduser("~/STARCORE")

registry={
    "component":"STARCORE SDK Registry",
    "version":"7.0.03",
    "modules":[]
}


with open(
f"{BASE}/registry/sdk_registry.json",
"w"
) as f:
    json.dump(registry,f,indent=4)


print("SDK API ONLINE")

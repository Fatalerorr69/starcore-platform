#!/usr/bin/env python3

import json
import os

BASE=os.path.expanduser("~/STARCORE")

registry={
    "platform":"STARCORE",
    "version":"7.0.01",
    "modules":[]
}

path=f"{BASE}/registry/modules.json"

with open(path,"w") as f:
    json.dump(registry,f,indent=4)

print("REGISTRY ONLINE")

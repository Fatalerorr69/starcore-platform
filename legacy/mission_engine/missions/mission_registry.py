#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


data={
    "component":"STARCORE Mission Registry",
    "version":"7.0.09",
    "missions":[],
    "status":"ready"
}


with open(
f"{BASE}/runtime/missions/mission_registry.json",
"w"
) as f:
    json.dump(data,f,indent=4)


print("MISSION REGISTRY ONLINE")

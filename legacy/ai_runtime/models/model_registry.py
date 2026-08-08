#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


data={
    "component":"STARCORE Model Registry",
    "version":"7.0.08",
    "models":[],
    "status":"ready"
}


with open(
f"{BASE}/runtime/ai/model_registry.json",
"w"
) as f:
    json.dump(data,f,indent=4)


print("MODEL REGISTRY ONLINE")

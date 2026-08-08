#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


data={
    "component":"STARCORE Workflow Engine",
    "version":"7.0.09",
    "workflows":[],
    "status":"online"
}


with open(
f"{BASE}/runtime/missions/workflow_state.json",
"w"
) as f:
    json.dump(data,f,indent=4)


print("WORKFLOW ENGINE ONLINE")

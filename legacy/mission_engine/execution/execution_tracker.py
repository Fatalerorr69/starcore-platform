#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


data={
    "component":"STARCORE Execution Tracker",
    "version":"7.0.09",
    "executions":[],
    "status":"ready"
}


with open(
f"{BASE}/runtime/missions/execution_state.json",
"w"
) as f:
    json.dump(data,f,indent=4)


print("EXECUTION TRACKER ONLINE")

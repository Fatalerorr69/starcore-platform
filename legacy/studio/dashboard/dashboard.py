#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


data={
    "component":"STARCORE Studio Dashboard",
    "version":"7.0.10",
    "modules":"all",
    "status":"online"
}


with open(
f"{BASE}/runtime/studio/dashboard_state.json",
"w"
) as f:
    json.dump(data,f,indent=4)


print("STUDIO DASHBOARD ONLINE")

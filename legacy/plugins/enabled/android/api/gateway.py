#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/api"
OUT.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE API Gateway",
"version":"6B.X.31",
"protocols":[
"local",
"ssh",
"tailscale"
],
"status":"online"
}


with open(OUT/"gateway_state.json","w") as f:
    json.dump(data,f,indent=4)

print("API GATEWAY READY")


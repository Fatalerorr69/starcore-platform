#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



profile={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Remote Profile",

"connection":{

"protocol":"SSH",

"port":8022,

"user":
"u0_a344",

"command":
"ssh -p 8022 u0_a344@TAILSCALE_IP"

},

"status":
"ready"

}



OUT=ROOT/"runtime/android/remote"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"remote_profile.json",
"w"
) as f:

    json.dump(
    profile,
    f,
    indent=4
    )


print("REMOTE PROFILE READY")


#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/remote"


try:
    ip=subprocess.check_output(
    "tailscale ip",
    shell=True,
    stderr=subprocess.DEVNULL
    ).decode().strip()

except:
    ip="unavailable"



json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"TAILSCALE PROFILE",
"tailscale_ip":ip,
"status":"ready"
},
open(OUT/"tailscale_profile.json","w"),
indent=4
)


print("TAILSCALE CHECK COMPLETE")


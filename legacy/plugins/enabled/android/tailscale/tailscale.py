#!/usr/bin/env python3


import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



def run(cmd):

    try:
        return subprocess.check_output(
        cmd,
        shell=True
        ).decode().strip()

    except:

        return "offline"



report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Tailscale Bridge",

"tailscale_ip":
run("tailscale ip 2>/dev/null"),

"status":
"detected"

}



OUT=ROOT/"runtime/android/remote"

OUT.mkdir(
parents=True,
exist_ok=True
)



with open(
OUT/"tailscale_status.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print("TAILSCALE READY")



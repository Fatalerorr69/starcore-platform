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
            shell=True,
            stderr=subprocess.STDOUT
        ).decode(errors="ignore").strip()

    except:

        return "unavailable"



data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE SSH Manager",

"sshd":
run("pgrep sshd"),

"port":
"8022",

"status":
"ready"

}



OUT=ROOT/"runtime/android/access"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"ssh_status.json",
"w"
) as f:

    json.dump(
    data,
    f,
    indent=4
    )


print("SSH READY")


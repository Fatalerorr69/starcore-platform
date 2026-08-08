#!/usr/bin/env python3

import os
import json
import subprocess
from datetime import datetime


BASE=os.path.expanduser("~/STARCORE")


def run(cmd):

    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True
        ).strip()

    except:
        return "unknown"



data={

    "component":
    "STARCORE Git Intelligence",

    "version":
    "7.0.15",

    "timestamp":
    datetime.utcnow().isoformat(),

    "repository":
    run("git remote -v"),

    "branch":
    run("git branch --show-current"),

    "commit":
    run("git rev-parse HEAD"),

    "status":
    "online"
}


with open(
f"{BASE}/runtime/github/repository_map.json",
"w"
) as f:

    json.dump(
        data,
        f,
        indent=4
    )


print("GITHUB INTELLIGENCE ONLINE")


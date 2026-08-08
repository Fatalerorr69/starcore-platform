#!/usr/bin/env python3

import os
import json
import platform
import subprocess
from datetime import datetime


BASE=os.path.expanduser("~/STARCORE")


def command(cmd):

    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True
        ).strip()

    except:
        return "unavailable"



report={

    "component":
    "STARCORE Environment Auditor",

    "version":
    "7.0.11",

    "timestamp":
    datetime.utcnow().isoformat(),

    "system":
    {
        "platform":
        platform.platform(),

        "python":
        command("python3 --version"),

        "node":
        command("node --version"),

        "npm":
        command("npm --version")
    },

    "storage":
    {
        "starcore_size":
        command("du -sh ~/STARCORE")
    },

    "status":
    "healthy"

}


with open(
f"{BASE}/runtime/hardening/environment_report.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print("ENVIRONMENT AUDITOR ONLINE")


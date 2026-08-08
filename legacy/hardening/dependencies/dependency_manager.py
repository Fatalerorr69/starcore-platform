#!/usr/bin/env python3

import json
import os
import subprocess


BASE=os.path.expanduser("~/STARCORE")


def get(cmd):

    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            text=True
        ).splitlines()

    except:
        return []


data={

"component":
"STARCORE Dependency Manager",

"version":
"7.0.12",

"python_packages":
get("pip list --format=freeze"),

"node_packages":
get("npm list -g --depth=0"),

"status":
"healthy"

}


with open(
f"{BASE}/runtime/hardening/dependency_health.json",
"w"
) as f:

    json.dump(
        data,
        f,
        indent=4
    )


print("DEPENDENCY MANAGER ONLINE")


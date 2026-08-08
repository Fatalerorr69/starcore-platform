#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


OUT=Path.home()/\
"STARCORE/runtime/android/network"


OUT.mkdir(
parents=True,
exist_ok=True
)



def run(c):

    try:
        return subprocess.check_output(
            c,
            shell=True
        ).decode(errors="ignore")

    except:
        return "unknown"



data={

"timestamp":
datetime.now().isoformat(),

"interfaces":
run("ip addr"),

"dns":
run("getprop | grep dns"),

"routes":
run("ip route"),

"connections":
run("netstat -tun 2>/dev/null")

}



with open(
OUT/"network_report.json",
"w"
) as f:

    json.dump(
    data,
    f,
    indent=4
    )


print(
"NETWORK INTELLIGENCE COMPLETE"
)


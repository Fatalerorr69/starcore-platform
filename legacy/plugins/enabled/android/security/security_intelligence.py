#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/security"

OUT.mkdir(
    parents=True,
    exist_ok=True
)



def cmd(x):

    try:
        return subprocess.check_output(
            x,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode(errors="ignore").strip()

    except:
        return "unavailable"



report={

"timestamp":datetime.now().isoformat(),

"boot":{

"verified":
cmd("getprop ro.boot.verifiedbootstate"),

"locked":
cmd("getprop ro.boot.flash.locked")

},


"selinux":
cmd("getenforce"),


"magisk":

Path("/data/adb").exists(),


"root":

cmd("id"),


"recommendations":[]

}



if report["magisk"]:

    report["recommendations"].append(
        "Root environment detected - maintain module audit"
    )


if report["selinux"]!="Enforcing":

    report["recommendations"].append(
        "SELinux is not enforcing"
    )


with open(
OUT/"security_report.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
"SECURITY INTELLIGENCE COMPLETE"
)


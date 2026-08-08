#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil


ROOT = Path.home() / "STARCORE"

OUT = ROOT / "runtime/android/network"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


def run(cmd, timeout=3):

    try:
        result = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=timeout
        )

        return result.decode(
            errors="ignore"
        ).strip()

    except Exception as e:
        return "unavailable"


report = {

    "timestamp":
        datetime.now().isoformat(),

    "network": {

        "interfaces":
            run("ip addr"),

        "routes":
            run("ip route"),

        "dns":
            run("getprop | grep dns"),

        "connections":
            run("cat /proc/net/tcp"),

        "wifi":
            run("termux-wifi-connectioninfo")

    },

    "environment": {

        "termux_api":
            shutil.which("termux-wifi-connectioninfo") is not None

    }

}


with open(
    OUT / "network_report_v2.json",
    "w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
    "NETWORK V2 COMPLETE"
)


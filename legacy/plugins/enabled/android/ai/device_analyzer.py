#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

SNAPSHOT_DIR = ROOT / "runtime/android/snapshots"
REPORT_DIR = ROOT / "runtime/android/reports"


REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def latest_snapshot():

    files = sorted(
        SNAPSHOT_DIR.glob("*.json")
    )

    if not files:
        return None

    return files[-1]


def analyze(data):

    result = {

        "timestamp":
            datetime.now().isoformat(),

        "health_score":100,

        "issues":[],

        "recommendations":[]

    }


    security=data.get(
        "security",
        {}
    )


    if security.get(
        "verified_boot"
    ) == "orange":

        result["health_score"] -= 20

        result["issues"].append(
            "Bootloader unlocked"
        )

        result["recommendations"].append(
            "Review root security configuration"
        )


    if security.get(
        "selinux"
    ) != "Enforcing":

        result["health_score"] -= 15

        result["issues"].append(
            "SELinux not enforcing"
        )


    device=data.get(
        "device",
        {}
    )


    result["recommendations"].append(
        "Enable regular STARCORE snapshots"
    )


    result["device"]=device


    return result



def main():

    snap=latest_snapshot()


    if not snap:

        print(
            "No snapshot available"
        )

        return


    with open(
        snap,
        "r"
    ) as f:

        data=json.load(f)



    report=analyze(data)


    output=REPORT_DIR / (
        "android_ai_report.json"
    )


    with open(
        output,
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    print(
        "AI ANALYSIS COMPLETE"
    )

    print(output)



if __name__=="__main__":
    main()


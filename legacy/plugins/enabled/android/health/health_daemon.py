#!/usr/bin/env python3

import json
import shutil
import os
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

OUT = ROOT / "runtime/android/health"

HISTORY = OUT / "history"

OUT.mkdir(
    parents=True,
    exist_ok=True
)

HISTORY.mkdir(
    parents=True,
    exist_ok=True
)



def storage():

    d = shutil.disk_usage(
        ROOT
    )

    return {

        "total": d.total,
        "used": d.used,
        "free": d.free

    }



def load_file(path):

    return path.exists()



def collect():

    report = {

        "timestamp":
            datetime.now().isoformat(),

        "component":
            "STARCORE Health Daemon",

        "version":
            "6B.X.3.C",

        "checks":
        {

            "runtime":
                load_file(
                    ROOT /
                    "runtime/android/runtime/runtime_manager.json"
                ),

            "events":
                load_file(
                    ROOT /
                    "runtime/android/events/history.json"
                ),

            "registry":
                load_file(
                    ROOT /
                    "runtime/android/registry/module_registry.json"
                )

        },

        "storage":
            storage(),

        "status":
            "healthy"

    }


    if not all(report["checks"].values()):

        report["status"]="warning"


    return report



def main():

    report = collect()


    with open(
        OUT/"health_daemon.json",
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    history_file = HISTORY / (
        datetime.now()
        .strftime("%Y%m%d_%H%M%S")
        +
        ".json"
    )


    with open(
        history_file,
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    print(
        "HEALTH DAEMON COMPLETE"
    )



if __name__=="__main__":
    main()


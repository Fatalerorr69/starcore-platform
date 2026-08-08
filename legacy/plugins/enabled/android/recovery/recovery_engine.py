#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

OUT = ROOT / "runtime/android/recovery"

HISTORY = OUT / "history"

OUT.mkdir(
    parents=True,
    exist_ok=True
)

HISTORY.mkdir(
    parents=True,
    exist_ok=True
)


REQUIRED = [

"runtime/android/registry",

"runtime/android/events",

"runtime/android/health",

"runtime/android/runtime",

"runtime/android/control"

]


def repair():

    actions=[]


    for item in REQUIRED:

        path = ROOT / item


        if not path.exists():

            path.mkdir(
                parents=True,
                exist_ok=True
            )

            actions.append(
                {
                    "action":"created",
                    "path":item
                }
            )


        else:

            actions.append(
                {
                    "action":"verified",
                    "path":item
                }
            )


    return actions



def main():

    report={

        "timestamp":
            datetime.now().isoformat(),

        "component":
            "STARCORE Recovery Engine",

        "version":
            "6B.X.3.D",

        "mode":
            "safe",

        "actions":
            repair(),

        "status":
            "healthy"

    }


    with open(
        OUT/"recovery_report.json",
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    history = HISTORY / (
        datetime.now()
        .strftime("%Y%m%d_%H%M%S")
        +
        ".json"
    )


    with open(
        history,
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    print(
        "RECOVERY ENGINE COMPLETE"
    )



if __name__=="__main__":
    main()


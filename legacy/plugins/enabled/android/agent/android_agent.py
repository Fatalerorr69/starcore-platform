#!/usr/bin/env python3


import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

EVENTS = ROOT / "runtime/android/events"

CONTEXT = ROOT / "runtime/android/context"


EVENTS.mkdir(
    parents=True,
    exist_ok=True
)

CONTEXT.mkdir(
    parents=True,
    exist_ok=True
)



def run_module(name, command):

    result={

        "module":name,

        "timestamp":
            datetime.now().isoformat(),

        "status":"started"

    }


    try:

        output=subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=60
        )

        result["status"]="success"

        result["output"]=(
            output.decode(
                errors="ignore"
            )[-2000:]
        )


    except Exception as e:

        result["status"]="failed"

        result["error"]=str(e)


    return result




def main():


    event=[]


    modules=[

        (
        "snapshot",
        "bash plugins/enabled/android/bin/snapshot.sh"
        ),

        (
        "optimization",
        "python plugins/enabled/android/optimization/optimizer.py"
        )

    ]



    for name,cmd in modules:

        event.append(
            run_module(
                name,
                cmd
            )
        )



    output=EVENTS / (
        "agent_event_"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".json"
    )


    with open(
        output,
        "w"
    ) as f:

        json.dump(
            event,
            f,
            indent=4
        )



    context=CONTEXT / "device_context.json"


    with open(
        context,
        "w"
    ) as f:

        json.dump(
            {
            "last_run":
            datetime.now().isoformat(),

            "events":
            str(output)
            },
            f,
            indent=4
        )


    print("ANDROID AGENT COMPLETE")

    print(output)




if __name__=="__main__":

    main()


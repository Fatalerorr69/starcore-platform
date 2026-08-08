#!/usr/bin/env python3

import json
import os
from datetime import datetime


BASE=os.path.expanduser("~/STARCORE")


def execute(command):

    result={
        "command":command,
        "timestamp":datetime.utcnow().isoformat(),
        "status":"success"
    }

    history=f"{BASE}/runtime/command_bus/command_history.json"

    data=[]

    if os.path.exists(history):
        with open(history) as f:
            data=json.load(f)

    data.append(result)

    with open(history,"w") as f:
        json.dump(data,f,indent=4)

    return result


if __name__=="__main__":

    print(json.dumps(
        execute("command_bus_test"),
        indent=4
    ))

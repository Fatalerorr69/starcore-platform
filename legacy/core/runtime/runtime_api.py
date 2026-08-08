#!/usr/bin/env python3

import os
import json
import platform
from datetime import datetime


ROOT=os.path.expanduser("~/STARCORE")


def runtime_status():

    return {

        "name":
            "STARCORE",

        "platform":
            "Android",

        "kernel":
            platform.release(),

        "architecture":
            platform.machine(),

        "time":
            datetime.utcnow().isoformat()+"Z"

    }



def save_status():

    path=os.path.join(
        ROOT,
        "runtime",
        "state",
        "runtime_status.json"
    )


    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )


    with open(path,"w") as f:

        json.dump(
            runtime_status(),
            f,
            indent=4
        )


    return path



if __name__=="__main__":

    print(
        json.dumps(
            runtime_status(),
            indent=4
        )
    )


#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime


ROOT=os.path.expanduser("~/STARCORE")

EVENT_DIR=os.path.join(
    ROOT,
    "runtime",
    "events"
)

EVENT_FILE=os.path.join(
    EVENT_DIR,
    "events.jsonl"
)


def ensure():

    os.makedirs(
        EVENT_DIR,
        exist_ok=True
    )



def emit(event,source="system",data=None):

    ensure()

    payload={
        "timestamp":
            datetime.utcnow().isoformat()+"Z",

        "event":
            event,

        "source":
            source,

        "data":
            data or {}
    }


    with open(EVENT_FILE,"a") as f:
        f.write(
            json.dumps(payload)
            + "\n"
        )


    print(
        json.dumps(
            payload,
            indent=2
        )
    )



def list_events():

    ensure()

    if not os.path.exists(EVENT_FILE):
        return


    with open(EVENT_FILE) as f:

        for line in f:

            print(line.strip())



if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "event_bus.py add|list"
        )

        sys.exit(1)



    cmd=sys.argv[1]


    if cmd=="add":

        emit(
            sys.argv[2]
            if len(sys.argv)>2
            else "unknown"
        )


    elif cmd=="list":

        list_events()


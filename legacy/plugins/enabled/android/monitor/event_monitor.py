#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


EVENTS=ROOT/"runtime/android/events/history.json"

OUT=ROOT/"runtime/android/monitor"

OUT.mkdir(
parents=True,
exist_ok=True
)


events=[]


if EVENTS.exists():

    with open(EVENTS) as f:
        events=json.load(f)



report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Event Monitor",

"version":
"6B.X.3.F",

"events_total":
len(events),

"last_event":
events[-1]
if events
else None,

"status":
"healthy"

}



with open(
OUT/"event_monitor.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print(
"EVENT MONITOR COMPLETE"
)


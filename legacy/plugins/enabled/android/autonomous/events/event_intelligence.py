#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/autonomous/events"

OUT.mkdir(parents=True,exist_ok=True)


event_file=ROOT/"runtime/android/events/history.json"


events=[]

if event_file.exists():

 with open(event_file) as f:
  events=json.load(f)


analysis={

"timestamp":datetime.now().isoformat(),

"events_total":len(events),

"priority":"normal",

"status":"analyzed"

}


with open(
OUT/"event_analysis.json",
"w"
) as f:

 json.dump(
 analysis,
 f,
 indent=4
 )


print("EVENT INTELLIGENCE READY")

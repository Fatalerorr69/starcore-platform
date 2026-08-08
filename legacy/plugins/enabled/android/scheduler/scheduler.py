#!/data/data/com.termux/files/usr/bin/python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


OUT=ROOT/"runtime/android/scheduler"


OUT.mkdir(
parents=True,
exist_ok=True
)


jobs_file=ROOT/"plugins/enabled/android/scheduler/jobs.json"


jobs=json.loads(
jobs_file.read_text()
)


state={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Scheduler",

"version":
"6B.X.12",

"jobs":
jobs,

"status":
"running"

}


(OUT/"scheduler_state.json").write_text(
json.dumps(
state,
indent=4
)
)


print(
"SCHEDULER ONLINE"
)


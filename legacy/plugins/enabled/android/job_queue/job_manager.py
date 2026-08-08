#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/job_queue"

OUT.mkdir(parents=True,exist_ok=True)


queue={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Job Queue V2",

"version":
"6B.X.34",

"jobs":[

{

"name":"health_check",

"status":"ready"

},

{

"name":"backup",

"status":"ready"

},

{

"name":"validation",

"status":"ready"

}

],

"status":
"ready"

}


with open(
OUT/"job_queue.json",
"w"
) as f:

    json.dump(
        queue,
        f,
        indent=4
    )


print("JOB QUEUE V2 READY")


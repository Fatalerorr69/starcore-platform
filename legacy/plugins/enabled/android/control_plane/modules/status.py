
#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


out=ROOT/"runtime/android/control_plane/status.json"


out.parent.mkdir(
parents=True,
exist_ok=True
)


data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Control Plane",

"version":
"6B.X.11",

"status":
"online"

}


json.dump(
data,
open(out,"w"),
indent=4
)


print(
"CONTROL PLANE ONLINE"
)


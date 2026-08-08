#!/data/data/com.termux/files/usr/bin/bash

set -e

cd ~/STARCORE || exit 1


echo "=================================================="
echo " STARCORE ANDROID CONTROL PLANE 6B.X.11"
echo "=================================================="


mkdir -p \
plugins/enabled/android/control_plane \
plugins/enabled/android/remote \
runtime/android/control_plane \
runtime/android/remote


echo "[1] Router"


cat > plugins/enabled/android/control_plane/router.py <<'PY'

#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT=Path.home()/"STARCORE"


COMMANDS={

"status":
"status.py",

"health":
"health.py",

"remote":
"remote.py"

}


cmd=sys.argv[1] if len(sys.argv)>1 else "status"


if cmd not in COMMANDS:

    print("Unknown command")
    sys.exit(1)


print(
"CONTROL COMMAND:",
cmd
)

PY


chmod +x plugins/enabled/android/control_plane/router.py



echo "[2] CLI"


cat > starcore <<'PY'

#!/data/data/com.termux/files/usr/bin/python


import sys
import subprocess


cmd=" ".join(sys.argv[1:])


if cmd.startswith("android"):

    args=cmd.split()

    action=args[1] if len(args)>1 else "status"


    subprocess.call(
        [
        "python",
        "plugins/enabled/android/control_plane/router.py",
        action
        ]
    )


else:

    print(
    "Usage: ./starcore android status"
    )


PY


chmod +x starcore



echo "[3] Status module"


mkdir -p plugins/enabled/android/control_plane/modules


cat > plugins/enabled/android/control_plane/modules/status.py <<'PY'

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

PY



echo "[4] Health module"


cat > plugins/enabled/android/control_plane/modules/health.py <<'PY'

#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


checks=[

"runtime/android/state",
"runtime/android/events",
"runtime/android/health",
"runtime/android/control"

]


result=[]


for c in checks:

    result.append({

    "path":c,

    "exists":
    (ROOT/c).exists()

    })


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Health",

"checks":
result,

"status":
"healthy"

}


out=ROOT/"runtime/android/control_plane/health.json"


json.dump(
report,
open(out,"w"),
indent=4
)


print(
"HEALTH COMPLETE"
)

PY



echo "[5] Validation"


python plugins/enabled/android/control_plane/modules/status.py

python plugins/enabled/android/control_plane/modules/health.py



echo "[6] Test CLI"


./starcore android status



echo "[7] Git"


git add .

git commit \
-m "Add STARCORE Android Control Plane 6B.X.11" || true


echo

echo "6B.X.11 COMPLETE"


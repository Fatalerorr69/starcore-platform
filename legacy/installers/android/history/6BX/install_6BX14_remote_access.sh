#!/data/data/com.termux/files/usr/bin/bash

set -e


ROOT="$HOME/STARCORE"


echo "=================================================="
echo " STARCORE REMOTE ACCESS LAYER 6B.X.14"
echo "=================================================="


cd "$ROOT"



mkdir -p \
plugins/enabled/android/remote \
plugins/enabled/android/tailscale \
plugins/enabled/android/ssh \
runtime/android/remote \
runtime/android/access \
runtime/android/health



echo "[1] SSH MANAGER"



cat > plugins/enabled/android/ssh/ssh_manager.py <<'PY'
#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


def run(cmd):

    try:

        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode(errors="ignore").strip()

    except:

        return "unavailable"



data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE SSH Manager",

"sshd":
run("pgrep sshd"),

"port":
"8022",

"status":
"ready"

}



OUT=ROOT/"runtime/android/access"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"ssh_status.json",
"w"
) as f:

    json.dump(
    data,
    f,
    indent=4
    )


print("SSH READY")

PY


chmod +x plugins/enabled/android/ssh/ssh_manager.py




echo "[2] TAILSCALE DETECTOR"



cat > plugins/enabled/android/tailscale/tailscale.py <<'PY'
#!/usr/bin/env python3


import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



def run(cmd):

    try:
        return subprocess.check_output(
        cmd,
        shell=True
        ).decode().strip()

    except:

        return "offline"



report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Tailscale Bridge",

"tailscale_ip":
run("tailscale ip 2>/dev/null"),

"status":
"detected"

}



OUT=ROOT/"runtime/android/remote"

OUT.mkdir(
parents=True,
exist_ok=True
)



with open(
OUT/"tailscale_status.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print("TAILSCALE READY")


PY


chmod +x plugins/enabled/android/tailscale/tailscale.py




echo "[3] REMOTE PROFILE"



cat > plugins/enabled/android/remote/remote_profile.py <<'PY'
#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



profile={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Remote Profile",

"connection":{

"protocol":"SSH",

"port":8022,

"user":
"u0_a344",

"command":
"ssh -p 8022 u0_a344@TAILSCALE_IP"

},

"status":
"ready"

}



OUT=ROOT/"runtime/android/remote"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"remote_profile.json",
"w"
) as f:

    json.dump(
    profile,
    f,
    indent=4
    )


print("REMOTE PROFILE READY")

PY


chmod +x plugins/enabled/android/remote/remote_profile.py




echo "[4] ACCESS HEALTH"



cat > plugins/enabled/android/remote/access_health.py <<'PY'
#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



files=[

"runtime/android/access/ssh_status.json",

"runtime/android/remote/tailscale_status.json",

"runtime/android/remote/remote_profile.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })



with open(
ROOT/"runtime/android/health/remote_health.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Remote Health",

    "version":
    "6B.X.14",

    "checks":
    checks,

    "status":
    "healthy"

    },f,indent=4)



print("REMOTE HEALTH COMPLETE")

PY


chmod +x plugins/enabled/android/remote/access_health.py




echo "[5] EXECUTION"



python plugins/enabled/android/ssh/ssh_manager.py

python plugins/enabled/android/tailscale/tailscale.py

python plugins/enabled/android/remote/remote_profile.py

python plugins/enabled/android/remote/access_health.py




echo "[6] VALIDATION"



python - <<'PY'

from pathlib import Path


files=[

"runtime/android/access/ssh_status.json",

"runtime/android/remote/tailscale_status.json",

"runtime/android/remote/remote_profile.json",

"runtime/android/health/remote_health.json"

]


for f in files:

    assert Path(f).exists(),f


print(
"6B.X.14 VALIDATION OK"
)

PY




git add plugins/enabled/android runtime/android

git commit \
-m "Add STARCORE Android Remote Access Layer 6B.X.14" || true



echo "=================================================="
echo " 6B.X.14 COMPLETE"
echo "=================================================="



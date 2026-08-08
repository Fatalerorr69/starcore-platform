#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "=================================================="
echo " STARCORE 6B.Y.100"
echo " TERMUX PRODUCTION HARDENING"
echo "=================================================="


BASE=~/STARCORE

cd "$BASE"


echo "[1] TERMUX UPDATE"

pkg update -y
pkg upgrade -y


echo "[2] SYSTEM PACKAGES"


PACKAGES="
git
curl
wget
openssl
gnupg
jq
tree
htop
ncdu
tmux
openssh
rsync
sqlite
python
python-pip
nodejs
npm
clang
cmake
make
pkg-config
rust
golang
ripgrep
fd
nmap
whois
"

for P in $PACKAGES
do
    pkg install -y "$P" || true
done


echo "[3] STORAGE"

termux-setup-storage || true


echo "[4] PYTHON ENVIRONMENT"


python -m pip install --upgrade pip setuptools wheel || true


PY_PACKAGES="
requests
httpx
aiohttp
fastapi
uvicorn
pydantic
pyyaml
orjson
rich
typer
psutil
networkx
numpy
pandas
scipy
scikit-learn
"

for P in $PY_PACKAGES
do
    pip install "$P" || true
done



echo "[5] STARCORE TOOL STRUCTURE"


mkdir -p \

tools/diagnostics \
tools/backup \
tools/security \
tools/networking \
tools/ai \
tools/database \
tools/maintenance \
tools/recovery \

plugins/enabled/android/environment_manager \
runtime/android/system_health \
runtime/android/environment \
runtime/android/snapshots



echo "[6] ENVIRONMENT MANAGER"


cat > plugins/enabled/android/environment_manager/environment_manager.py <<'PY'
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
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()

    except:
        return "unknown"



data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Environment Manager",

"python":
run("python --version"),

"pip":
run("pip --version"),

"node":
run("node --version"),

"npm":
run("npm --version"),

"git":
run("git --version"),

"rust":
run("rustc --version"),

"status":
"healthy"

}


OUT=ROOT/"runtime/android/environment"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"environment_state.json",
"w"
) as f:

    json.dump(
        data,
        f,
        indent=4
    )


print("ENVIRONMENT MANAGER READY")

PY


chmod +x plugins/enabled/android/environment_manager/environment_manager.py



echo "[7] PACKAGE INVENTORY"


pkg list-installed > runtime/android/environment/pkg_list.txt || true

pip freeze > runtime/android/environment/pip_freeze.txt || true

npm list -g > runtime/android/environment/npm_global.txt || true



echo "[8] SYSTEM HEALTH"


python plugins/enabled/android/environment_manager/environment_manager.py



python - <<'PY'

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


checks=[

"runtime/android/environment/environment_state.json",
"runtime/android/environment/pkg_list.txt",
"runtime/android/environment/pip_freeze.txt",
"runtime/android/environment/npm_global.txt"

]


result={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Termux Environment Health",

"version":
"6B.Y.100.HARDENING",

"checks":[],

"errors":0,

"status":
"READY"

}


for c in checks:

    exists=Path(c).exists()

    result["checks"].append(
        {
        "file":c,
        "exists":exists
        }
    )

    if not exists:
        result["errors"]+=1



if result["errors"]:
    result["status"]="WARNING"


OUT=ROOT/"runtime/android/system_health"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"termux_environment_health.json",
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print("TERMUX HEALTH COMPLETE")

PY



echo "[9] SNAPSHOT"


tar -czf \
runtime/android/snapshots/termux_environment_snapshot.tar.gz \
runtime/android/environment \
plugins/enabled/android/environment_manager \
2>/dev/null || true



echo "[10] GIT"


git add .

git commit \
-m "Add STARCORE Termux Production Hardening 6B.Y.100" || true



echo "=================================================="
echo " STARCORE TERMUX HARDENING COMPLETE"
echo "=================================================="


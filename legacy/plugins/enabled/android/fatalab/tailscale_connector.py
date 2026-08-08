#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/fatalab"

OUT.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Tailscale Connector",
"version":"6B.Y.6",
"protocol":"tailscale",
"status":"ready"
}


json.dump(
data,
open(OUT/"tailscale_connector.json","w"),
indent=4
)

print("TAILSCALE CONNECTOR READY")


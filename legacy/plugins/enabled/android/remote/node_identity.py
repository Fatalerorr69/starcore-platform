#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime
import socket


root=Path.home()/"STARCORE"

out=root/"runtime/android/remote_intelligence"
out.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Remote Node Identity",
"version":"6B.Y.21",
"node":socket.gethostname(),
"role":"android_edge_node",
"status":"registered"
}


json.dump(
data,
open(out/"node_identity.json","w"),
indent=4
)

print("NODE IDENTITY READY")

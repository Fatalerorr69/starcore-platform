#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/security_intelligence/incidents"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Incident Response",
"incidents":[],
"status":"ready"
},
open(out/"incident_state.json","w"),
indent=4
)

print("INCIDENT RESPONSE READY")

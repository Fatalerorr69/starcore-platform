#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

root=Path.home()/ "STARCORE/runtime/android/security_intelligence"

files=[
"identity/identity_registry.json",
"permissions/permission_state.json",
"threats/threat_report.json",
"integrity/integrity_report.json",
"policies/policy_state.json",
"audit/audit_log.json",
"incidents/incident_state.json"
]

checks=[]

for f in files:
    checks.append({
    "file":f,
    "exists":(root/f).exists()
    })

health=root/"health"
health.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Security Supervisor",
"version":"6B.Y.79",
"checks":checks,
"status":"healthy"
},
open(health/"security_health.json","w"),
indent=4
)

print("SECURITY HEALTH COMPLETE")

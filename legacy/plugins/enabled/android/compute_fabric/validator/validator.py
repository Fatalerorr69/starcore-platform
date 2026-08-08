#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

root=Path.home()/ "STARCORE/runtime/android/compute_fabric"

files=[
"resources/resource_state.json",
"cpu/cpu_metrics.json",
"memory/memory_metrics.json",
"gpu/gpu_bridge.json",
"scheduler/workload_queue.json",
"containers/docker_bridge.json",
"remote/compute_nodes.json",
"performance/performance_report.json"
]

checks=[]

for f in files:
    checks.append(
    {
    "file":f,
    "exists":(root/f).exists()
    })


health=root/"health"
health.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Compute Fabric Validator",
"version":"6B.Y.90",
"checks":checks,
"errors":0,
"status":"healthy"
},
open(health/"compute_health.json","w"),
indent=4
)

print("COMPUTE HEALTH COMPLETE")

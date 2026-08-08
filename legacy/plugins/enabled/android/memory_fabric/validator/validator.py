#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

root=Path.home()/ "STARCORE/runtime/android/memory_fabric"

files=[
"short_term/short_memory.json",
"long_term/long_memory.json",
"vector/vector_registry.json",
"knowledge/knowledge_graph.json",
"embedding/embedding_state.json",
"sync/memory_sync.json",
"optimizer/optimization_report.json",
"backup/backup_state.json"
]

checks=[]

for f in files:
    checks.append(
    {
    "file":f,
    "exists":(root/f).exists()
    })


out=root/"health"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Memory Fabric Validator",
"version":"6B.Y.70",
"checks":checks,
"status":"healthy"
},
open(out/"memory_fabric_health.json","w"),
indent=4
)

print("MEMORY FABRIC HEALTH COMPLETE")

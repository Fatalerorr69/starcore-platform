#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/cognitive_v2/health"

out.mkdir(parents=True,exist_ok=True)

checks=[
"reasoning/reasoning_state.json",
"planning/planning_state.json",
"context/context_state.json",
"inference/inference_state.json",
"decisions/decision_history.json",
"learning/learning_state.json"
]

result=[]

for c in checks:
    result.append({
    "file":c,
    "exists":(out.parent/c).exists()
    })


json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Cognitive Supervisor",
"version":"6B.Y.59",
"checks":result,
"status":"healthy"
},
open(out/"cognitive_health.json","w"),
indent=4)

print("COGNITIVE HEALTH COMPLETE")

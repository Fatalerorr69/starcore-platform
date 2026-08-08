#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/memory_fabric/knowledge"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Knowledge Graph",
"nodes":0,
"edges":0,
"status":"online"
},
open(out/"knowledge_graph.json","w"),
indent=4
)

print("KNOWLEDGE GRAPH ONLINE")

#!/usr/bin/env python3

import json
import os


BASE=os.path.expanduser("~/STARCORE")


state={
    "component":"STARCORE Inference Engine",
    "version":"7.0.08",
    "backend":"ready",
    "providers":[
        "ollama",
        "local"
    ],
    "status":"online"
}


with open(
f"{BASE}/runtime/ai/inference_state.json",
"w"
) as f:
    json.dump(state,f,indent=4)


print("INFERENCE ENGINE ONLINE")

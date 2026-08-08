#!/usr/bin/env python3

import json
import os
from datetime import datetime

BASE=os.path.expanduser("~/STARCORE")

def write_state():
    state={
        "component":"STARCORE Installer Engine",
        "version":"7.0.01",
        "timestamp":datetime.utcnow().isoformat(),
        "status":"online"
    }

    path=f"{BASE}/runtime/platform/installer_state.json"

    with open(path,"w") as f:
        json.dump(state,f,indent=4)


if __name__=="__main__":
    write_state()
    print("INSTALLER ENGINE ONLINE")

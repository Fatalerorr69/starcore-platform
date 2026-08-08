#!/usr/bin/env python3

import os
from datetime import datetime

path=os.path.expanduser(
"~/STARCORE/runtime/logs/installer.log"
)

with open(path,"a") as f:
    f.write(
        datetime.utcnow().isoformat()
        +" STARCORE INSTALLER STARTED\n"
    )

print("LOGGER ONLINE")

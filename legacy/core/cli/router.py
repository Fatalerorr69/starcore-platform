#!/usr/bin/env python3

import sys
import json
import os

BASE=os.path.expanduser("~/STARCORE")


command=sys.argv[1] if len(sys.argv)>1 else "status"


if command=="status":

    print("================================")
    print(" STARCORE PLATFORM")
    print("================================")

    print("CLI CORE: ONLINE")
    print("COMMAND BUS: ONLINE")

elif command=="health":

    path=f"{BASE}/runtime/platform/health.json"

    if os.path.exists(path):
        print(open(path).read())

elif command=="logs":

    path=f"{BASE}/runtime/logs/installer.log"

    if os.path.exists(path):
        print(open(path).read())

else:

    print("Unknown command:",command)

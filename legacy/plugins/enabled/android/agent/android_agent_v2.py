#!/usr/bin/env python3


import subprocess
from datetime import datetime


modules=[

"python plugins/enabled/android/security/security_intelligence.py",

"python plugins/enabled/android/network/network_intelligence.py",

"python plugins/enabled/android/audit/integrity_audit.py"

]


print(
"STARCORE ANDROID AGENT v2"
)


for m in modules:

    print(
    "\nRUN:",
    m
    )

    subprocess.call(
        m,
        shell=True
    )


print(
"\nAGENT COMPLETE",
datetime.now()
)



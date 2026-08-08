
#!/usr/bin/env python3

import sys
from pathlib import Path


ROOT=Path.home()/"STARCORE"


COMMANDS={

"status":
"status.py",

"health":
"health.py",

"remote":
"remote.py"

}


cmd=sys.argv[1] if len(sys.argv)>1 else "status"


if cmd not in COMMANDS:

    print("Unknown command")
    sys.exit(1)


print(
"CONTROL COMMAND:",
cmd
)


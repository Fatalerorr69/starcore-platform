import json,os

base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Autonomous Recovery System",
"version":"7.2.09",
"recovery":"enabled",
"status":"healthy"
},
open(base+"/runtime/autonomous_recovery.json","w"),
indent=4)

print("RECOVERY ONLINE")

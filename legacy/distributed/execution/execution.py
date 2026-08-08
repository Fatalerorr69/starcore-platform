import json,os

base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Remote Execution Engine",
"version":"7.2.08",
"jobs":[],
"status":"ready"
},
open(base+"/runtime/remote_execution.json","w"),
indent=4)

print("REMOTE EXECUTION READY")

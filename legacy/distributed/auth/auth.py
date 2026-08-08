import json,os

base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Remote Node Authentication",
"version":"7.2.02",
"identity":"enabled",
"tokens":[],
"status":"ready"
},
open(base+"/runtime/distributed_auth.json","w"),
indent=4)

print("NODE AUTH ONLINE")

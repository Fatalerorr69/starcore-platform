import json,os

base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Agent Communication Bus",
"version":"7.2.03",
"channels":[],
"status":"online"
},
open(base+"/runtime/agent_bus.json","w"),
indent=4)

print("AGENT BUS ONLINE")

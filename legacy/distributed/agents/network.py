import json,os
base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Distributed Agent Network",
"version":"7.2.01",
"nodes":[],
"agents":[],
"status":"online"
},
open(base+"/runtime/distributed_agent_network.json","w"),
indent=4)

print("AGENT NETWORK ONLINE")

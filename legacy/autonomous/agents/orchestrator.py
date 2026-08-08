import json,os

base=os.path.expanduser("~/STARCORE")

data={
"component":"STARCORE Agent Orchestrator",
"version":"7.1.01",
"agents":[],
"status":"online"
}

json.dump(
data,
open(base+"/runtime/autonomous/agent_registry.json","w"),
indent=4
)

print("AGENT ORCHESTRATOR ONLINE")

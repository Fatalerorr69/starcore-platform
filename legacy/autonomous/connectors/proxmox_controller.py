import json,os

base=os.path.expanduser("~/STARCORE")

json.dump(
{
"component":"Proxmox Controller",
"version":"7.1.07",
"nodes":[],
"status":"ready"
},
open(base+"/runtime/autonomous/proxmox_state.json","w"),
indent=4
)

print("PROXMOX CONTROLLER READY")

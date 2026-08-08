import json,os

base=os.path.expanduser("~/STARCORE")

json.dump(
{
"component":"Distributed Node Mesh",
"version":"7.1.08",
"nodes":[],
"status":"ready"
},
open(base+"/runtime/autonomous/node_mesh.json","w"),
indent=4
)

print("NODE MESH READY")

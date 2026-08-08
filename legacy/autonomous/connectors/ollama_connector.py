import json,os

base=os.path.expanduser("~/STARCORE")

json.dump(
{
"component":"Ollama Connector",
"version":"7.1.05",
"endpoint":"localhost:11434",
"status":"ready"
},
open(base+"/runtime/autonomous/ollama_connector.json","w"),
indent=4
)

print("OLLAMA CONNECTOR READY")

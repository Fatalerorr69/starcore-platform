import json,os

base=os.path.expanduser("~/STARCORE")

json.dump({
"component":"Event Streaming Layer",
"version":"7.2.04",
"events":[],
"status":"ready"
},
open(base+"/runtime/event_stream.json","w"),
indent=4)

print("EVENT STREAM ONLINE")

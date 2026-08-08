import json,os

base=os.path.expanduser("~/STARCORE")

json.dump(
{
"component":"Autonomous Scheduler",
"version":"7.1.03",
"tasks":[],
"status":"ready"
},
open(base+"/runtime/autonomous/task_scheduler.json","w"),
indent=4
)

print("TASK SCHEDULER ONLINE")

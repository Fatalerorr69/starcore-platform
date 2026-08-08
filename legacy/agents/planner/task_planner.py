import json

def create_task(name):
    return {
        "task":name,
        "status":"queued"
    }

print(json.dumps(create_task("system_task"),indent=4))

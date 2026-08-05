from datetime import datetime
from pathlib import Path

LOG=Path.home()/ "STARCORE/core/logs/starcore.log"

def write(module,event,status="OK"):

    LOG.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(LOG,"a") as f:
        f.write(
            f"{datetime.now()} | {module} | {event} | {status}\n"
        )


if __name__=="__main__":
    write(
        "system",
        "logger_test"
    )

    print("log created")

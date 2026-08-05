import json

from datetime import datetime
from pathlib import Path

from device import collect as device_collect
from resources import collect as resource_collect
from security import collect as security_collect
from network import collect as network_collect
from battery import collect as battery_collect
from packages import collect as package_collect
from storage import collect as storage_collect
from properties import collect as property_collect


REPORT=Path.home()/\
"STARCORE/security/reports/device_audit.json"



def run():

    data={

        "timestamp":
            str(datetime.now()),

        "device":
            device_collect(),

        "properties":
            property_collect(),

        "resources":
            resource_collect(),

        "storage":
            storage_collect(),

        "battery":
            battery_collect(),

        "packages":
            package_collect(),

        "security":
            security_collect(),

        "network":
            network_collect()

    }


    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    REPORT.write_text(
        json.dumps(
            data,
            indent=4
        )
    )


    print(
        "Audit saved:",
        REPORT
    )


if __name__=="__main__":

    run()

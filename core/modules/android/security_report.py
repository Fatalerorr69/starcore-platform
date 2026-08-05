import json
from datetime import datetime
from pathlib import Path

from security_intel import collect


REPORT=Path.home()/\
"STARCORE/security/reports/security_report.json"



def generate():

    data={

        "timestamp":
            str(datetime.now()),

        "security":
            collect()

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
        "Security report saved:",
        REPORT
    )


if __name__=="__main__":

    generate()


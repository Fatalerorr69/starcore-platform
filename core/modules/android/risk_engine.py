import json

from datetime import datetime
from pathlib import Path

from magisk import collect as magisk_collect
from root import collect as root_collect
from integrity_engine import scan as integrity_scan


REPORT=Path.home()/\
"STARCORE/security/dashboard/risk_analysis.json"



def add_finding(
    findings,
    name,
    points,
    severity
):

    findings.append(
        {
            "name":name,
            "points":points,
            "severity":severity
        }
    )

    return points



def calculate():

    score=0
    findings=[]


    root=root_collect()
    magisk=magisk_collect()
    integrity=integrity_scan()



    if root.get(
        "root_available"
    ):

        score += add_finding(
            findings,
            "ROOT ACCESS",
            15,
            "HIGH"
        )



    if "MAGISK" in str(
        magisk
    ):

        score += add_finding(
            findings,
            "MAGISK FRAMEWORK",
            10,
            "MEDIUM"
        )



    if integrity.get(
        "play_integrity_fix"
    ):

        score += add_finding(
            findings,
            "PLAY INTEGRITY FIX",
            10,
            "MEDIUM"
        )



    if integrity.get(
        "tricky_store"
    ):

        score += add_finding(
            findings,
            "TRICKY STORE",
            10,
            "HIGH"
        )



    if integrity.get(
        "zygisk_assistant"
    ):

        score += add_finding(
            findings,
            "ZYGISK ASSISTANT",
            5,
            "MEDIUM"
        )



    if score >=70:
        risk="CRITICAL"

    elif score >=50:
        risk="HIGH"

    elif score >=30:
        risk="MEDIUM"

    else:
        risk="LOW"



    return {

        "timestamp":
            str(datetime.now()),

        "score":
            score,

        "risk":
            risk,

        "findings":
            findings,

        "integrity":
            integrity
    }




def run():

    data=calculate()


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
        json.dumps(
            data,
            indent=4
        )
    )



if __name__=="__main__":
    run()


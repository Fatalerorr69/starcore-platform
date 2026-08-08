import json
from datetime import datetime
from pathlib import Path

from security_intel import collect as security_collect
from root import collect as root_collect
from magisk import collect as magisk_collect
from properties import collect as property_collect
from packages import collect as package_collect


REPORT = Path.home()/\
"STARCORE/security/dashboard/security_status.json"



def analyze_root(data):

    if data.get("root_available"):
        return "ACTIVE"

    return "NOT_DETECTED"



def analyze_magisk(data):

    version=data.get(
        "magisk",
        {}
    ).get(
        "version",
        ""
    )

    if "MAGISK" in version:
        return version

    return "UNKNOWN"



def calculate_score(
    root,
    magisk,
    security
):

    score=0
    findings=[]


    if root=="ACTIVE":

        score+=15
        findings.append(
            "ROOT ACCESS ENABLED"
        )


    if "MAGISK" in magisk:

        score+=10
        findings.append(
            "MAGISK DETECTED"
        )


    if security["integrity"].get(
        "play_integrity_fix"
    ):

        score+=10
        findings.append(
            "PLAY INTEGRITY FIX"
        )


    if security["integrity"].get(
        "tricky_store"
    ):

        score+=10
        findings.append(
            "TRICKY STORE"
        )


    selinux=security.get(
        "selinux",
        {}
    ).get(
        "status",
        ""
    )


    if selinux!="Enforcing":

        score+=25
        findings.append(
            "SELINUX NOT ENFORCING"
        )


    return score,findings



def run():


    security=security_collect()

    root=root_collect()

    magisk=magisk_collect()

    props=property_collect()

    packages=package_collect()


    root_status=analyze_root(
        root
    )


    magisk_status=analyze_magisk(
        magisk
    )


    score,findings=calculate_score(
        root_status,
        magisk_status,
        security
    )


    if score >=60:
        risk="HIGH"

    elif score >=30:
        risk="MEDIUM"

    else:
        risk="LOW"



    report={

        "timestamp":
            str(datetime.now()),

        "device":
            props,

        "root":
            root_status,

        "magisk":
            magisk_status,

        "package_count":
            packages.get(
                "count",
                0
            ),

        "security_score":
            score,

        "risk":
            risk,

        "findings":
            findings

    }



    REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    REPORT.write_text(
        json.dumps(
            report,
            indent=4
        )
    )


    print(
        json.dumps(
            report,
            indent=4
        )
    )


if __name__=="__main__":
    run()


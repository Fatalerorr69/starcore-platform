#!/usr/bin/env python3

import json
import shutil
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"

OUT = ROOT / "runtime/android/optimization"

OUT.mkdir(
    parents=True,
    exist_ok=True
)



def storage():

    usage = shutil.disk_usage(
        Path.home()
    )

    return {

        "total":
            usage.total,

        "used":
            usage.used,

        "free":
            usage.free

    }



def analyze():


    result={

        "timestamp":
            datetime.now().isoformat(),

        "storage":
            storage(),

        "recommendations":[],

        "optimization_score":100

    }


    free=result["storage"]["free"]

    total=result["storage"]["total"]


    percent=(free/total)*100


    if percent < 15:

        result["optimization_score"]-=30

        result["recommendations"].append(
            "Low storage available"
        )


    result["recommendations"].append(
        "Review Termux package updates"
    )


    result["recommendations"].append(
        "Maintain periodic STARCORE snapshots"
    )


    return result




def main():

    report=analyze()


    output=OUT / "optimization_report.json"


    with open(
        output,
        "w"
    ) as f:

        json.dump(
            report,
            f,
            indent=4
        )


    print(
        "OPTIMIZATION ANALYSIS COMPLETE"
    )

    print(output)



if __name__=="__main__":

    main()


#!/usr/bin/env python3


import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/termux"


OUT.mkdir(
    parents=True,
    exist_ok=True
)



def command(cmd):

    try:

        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=20
        ).decode(
            errors="ignore"
        )

    except Exception as e:

        return str(e)



def main():

    report={

        "timestamp":
        datetime.now().isoformat(),

        "termux":{},

        "runtime":{},

        "recommendations":[]

    }


    report["termux"]["prefix"]=command(
        "echo $PREFIX"
    )


    report["termux"]["home"]=command(
        "echo $HOME"
    )


    report["runtime"]["python"]=command(
        "python --version"
    )


    report["runtime"]["node"]=command(
        "node --version"
    )


    report["runtime"]["disk"]=str(
        shutil.disk_usage(
            Path.home()
        )
    )


    report["packages"]=command(
        "pkg list-installed | head -50"
    )


    if shutil.disk_usage(Path.home()).free < 10*1024**3:

        report["recommendations"].append(
            "Low storage space"
        )


    report["recommendations"].append(
        "Enable Termux:Boot integration"
    )


    output=OUT/"termux_intelligence.json"


    with open(output,"w") as f:

        json.dump(
            report,
            f,
            indent=4
        )


    print("TERMUX INTELLIGENCE COMPLETE")
    print(output)



if __name__=="__main__":

    main()


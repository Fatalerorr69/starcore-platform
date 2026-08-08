import os
import subprocess
import json

from pathlib import Path


REPORT=Path.home()/\
"STARCORE/security/dashboard/integrity_status.json"



def root(cmd):

    try:

        return subprocess.check_output(
            f"su -c '{cmd}'",
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

    except:

        return "ERROR"



def exists(path):

    return root(
        f"test -e {path} && echo YES"
    )=="YES"



def list_modules():

    data=root(
        "ls /data/adb/modules"
    )

    if data=="ERROR":
        return []

    return data.splitlines()



def scan():

    modules=list_modules()


    result={

        "modules":
            modules,


        "play_integrity_fix":
            "playintegrityfix" in modules,


        "tricky_store":
            "tricky_store" in modules,


        "zygisk_assistant":
            "zygisk-assistant" in modules,


        "files":{

            "custom_pif_prop":
                exists(
                "/data/adb/modules/playintegrityfix/custom.pif.prop"
                ),

            "target_txt":
                exists(
                "/data/adb/tricky_store/target.txt"
                ),

            "keybox":
                exists(
                "/data/adb/tricky_store/keybox.xml"
                )

        }

    }


    return result



def run():

    data=scan()


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


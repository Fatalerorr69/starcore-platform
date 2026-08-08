import os
import subprocess
from pathlib import Path



def cmd(command):

    try:

        return subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

    except:

        return "unknown"



def read(path):

    try:

        return Path(path).read_text().strip()

    except:

        return "unknown"



def collect():

    base="/data/adb"


    modules=[]


    module_path=f"{base}/modules"


    if os.path.exists(module_path):

        for item in os.listdir(module_path):

            modules.append(item)



    return {


        "magisk":

        {

            "path_exists":
                os.path.exists(base),

            "version":
                cmd(
                "su -c magisk -v"
                ),

            "zygisk":

                cmd(
                "su -c getprop ro.zygisk.enabled"
                )

        },


        "modules":

            modules,


        "mount":

            cmd(
            "su -c mount | grep magisk"
            )[:1000]


    }



if __name__=="__main__":

    print(collect())

import os
import subprocess


def cmd(command):

    try:
        return subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

    except Exception as e:

        return "ERROR"



def collect():

    su_paths=[
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/data/adb/magisk"
    ]


    found=[]


    for path in su_paths:

        if os.path.exists(path):

            found.append(path)



    uid=cmd("id")

    root_test=cmd(
        "su -c id"
    )


    return {

        "su_paths":found,

        "uid":
            uid,

        "su_test":
            root_test,

        "root_available":
            "uid=0" in root_test

    }



if __name__=="__main__":

    print(collect())

import subprocess
import os


def cmd(command):

    try:
        return subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

    except:
        return "ERROR"



def root_cmd(command):

    return cmd(
        f"su -c '{command}'"
    )



def exists_any(paths):

    found=[]

    for p in paths:

        if os.path.exists(p):
            found.append(p)

    return found



def collect():

    return {

        "root": {

            "normal":
                cmd("id"),

            "root":
                root_cmd("id")

        },


        "magisk": {

            "version":
                root_cmd("magisk -v"),

            "zygisk":
                exists_any([
                    "/system/lib/libzygisk.so",
                    "/system/lib64/libzygisk.so"
                ]),

            "modules":
                cmd(
                "su -c 'ls /data/adb/modules'"
                )

        },


        "kernelsu": {

            "detected":
                exists_any([
                    "/data/adb/ksu",
                    "/data/adb/ksud"
                ])

        },


        "boot": {

            "verifiedboot_normal":
                cmd(
                "getprop ro.boot.verifiedbootstate"
                ),

            "verifiedboot_root":
                root_cmd(
                "getprop ro.boot.verifiedbootstate"
                ),

            "flash_locked":
                cmd(
                "getprop ro.boot.flash.locked"
                )

        },


        "selinux": {

            "status":
                root_cmd(
                "getenforce"
                )

        },


        "integrity": {

            "play_integrity_fix":
                exists_any([
                    "/data/adb/modules/playintegrityfix",
                    "/data/adb/modules/playintegrityfixnext"
                ]),

            "tricky_store":
                exists_any([
                    "/data/adb/tricky_store",
                    "/data/adb/modules/tricky_store"
                ])

        }

    }



if __name__=="__main__":

    print(collect())


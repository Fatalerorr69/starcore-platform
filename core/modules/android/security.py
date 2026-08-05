import os


def collect():

    paths=[
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su"
    ]

    root=False

    for p in paths:
        if os.path.exists(p):
            root=True


    magisk=os.path.exists(
        "/data/adb/magisk"
    )

    return {
        "root_binary":root,
        "magisk_detected":magisk
    }

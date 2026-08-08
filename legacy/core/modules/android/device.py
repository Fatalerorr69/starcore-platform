import subprocess


def cmd(command):
    try:
        return subprocess.check_output(
            command,
            shell=True,
            text=True
        ).strip()
    except:
        return "unknown"


def collect():

    return {
        "model": cmd("getprop ro.product.model"),
        "brand": cmd("getprop ro.product.brand"),
        "android": cmd("getprop ro.build.version.release"),
        "sdk": cmd("getprop ro.build.version.sdk"),
        "kernel": cmd("uname -r"),
        "arch": cmd("uname -m")
    }

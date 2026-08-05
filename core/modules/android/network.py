import subprocess


def collect():

    try:
        ip=subprocess.check_output(
            "ip addr",
            shell=True,
            text=True
        )

    except:
        ip="unknown"


    return {
        "interfaces":ip[:500]
    }

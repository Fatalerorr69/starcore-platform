import subprocess


ANDROID_BIN="/system/bin"


def run(command):

    try:

        result=subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        )

        return result.strip()

    except Exception as e:

        return "ERROR: " + str(e)



def dumpsys(service):

    return run(
        f"{ANDROID_BIN}/dumpsys {service}"
    )



def pm(command):

    return run(
        f"{ANDROID_BIN}/pm {command}"
    )



def getprop(prop):

    return run(
        f"{ANDROID_BIN}/getprop {prop}"
    )



if __name__=="__main__":

    print(
        getprop(
            "ro.product.model"
        )
    )

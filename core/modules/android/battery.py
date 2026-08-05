import os
import subprocess


def run_root(cmd):

    try:

        return subprocess.check_output(
            f"su -c '{cmd}'",
            shell=True,
            stderr=subprocess.STDOUT,
            text=True
        ).strip()

    except Exception as e:

        return "ERROR:" + str(e)



def read_file(path):

    try:

        with open(path) as f:
            return f.read().strip()

    except:

        return "unknown"



def collect_dumpsys():

    data=run_root(
        "/system/bin/dumpsys battery"
    )


    if (
        "Can't find service" in data
        or
        data.startswith("ERROR")
        or
        len(data)<20
    ):
        return None


    result={}


    for line in data.splitlines():

        if ":" in line:

            key,value=line.split(
                ":",
                1
            )

            result[key.strip()] = value.strip()


    return result



def collect_sysfs():

    base="/sys/class/power_supply"

    result={}


    if not os.path.exists(base):

        return {
            "error":"no power_supply"
        }


    for device in os.listdir(base):

        path=f"{base}/{device}"

        result[device]={}


        for item in [

            "capacity",
            "status",
            "health",
            "voltage_now",
            "current_now",
            "temp"

        ]:

            result[device][item]=read_file(
                f"{path}/{item}"
            )


    return result



def collect():

    dumpsys=collect_dumpsys()


    if dumpsys:

        return {

            "source":"root_dumpsys",
            "data":dumpsys

        }


    return {

        "source":"sysfs",
        "data":collect_sysfs()

    }



if __name__=="__main__":

    print(collect())

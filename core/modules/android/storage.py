import shutil
import os


def collect():

    path=os.path.expanduser("~")

    total,used,free=shutil.disk_usage(path)

    return {

        "total_gb":
            round(total/1024**3,2),

        "used_gb":
            round(used/1024**3,2),

        "free_gb":
            round(free/1024**3,2)
    }


if __name__=="__main__":
    print(collect())

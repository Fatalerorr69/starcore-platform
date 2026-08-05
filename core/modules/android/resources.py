import shutil
import os


def collect():

    total,used,free = shutil.disk_usage(
        os.path.expanduser("~")
    )

    return {
        "storage_total_gb": round(total/1024**3,2),
        "storage_used_gb": round(used/1024**3,2),
        "storage_free_gb": round(free/1024**3,2)
    }

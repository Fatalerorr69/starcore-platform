import subprocess


def collect():

    try:

        ps=subprocess.check_output(
            "ps -A",
            shell=True,
            text=True
        )

        lines=ps.splitlines()

        return {
            "process_count":len(lines),
            "sample":lines[:50]
        }

    except Exception as e:

        return {
            "error":str(e)
        }


if __name__=="__main__":
    print(collect())

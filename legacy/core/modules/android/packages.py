from android_cmd import pm


def collect():

    data=pm(
        "list packages"
    )


    if data.startswith("ERROR"):

        return {
            "error":data
        }


    packages=[]


    for line in data.splitlines():

        if line.startswith("package:"):

            packages.append(
                line.replace(
                    "package:",
                    ""
                )
            )


    return {

        "count":
            len(packages),

        "packages":
            packages[:100]

    }



if __name__=="__main__":

    print(
        collect()
    )

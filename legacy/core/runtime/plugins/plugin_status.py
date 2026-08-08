#!/usr/bin/env python3

import os
import json


ROOT=os.path.expanduser("~/STARCORE")

PLUGIN_ROOT=os.path.join(
    ROOT,
    "plugins"
)


def scan():

    result=[]


    for state in [
        "enabled",
        "disabled"
    ]:

        path=os.path.join(
            PLUGIN_ROOT,
            state
        )


        if os.path.exists(path):

            for item in os.listdir(path):

                result.append(
                    {
                    "name":item,
                    "status":state
                    }
                )


    return result



if __name__=="__main__":

    print(
        json.dumps(
            scan(),
            indent=4
        )
    )


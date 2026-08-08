#!/usr/bin/env python3

import os
import json
import sys
import shutil


ROOT=os.path.expanduser("~/STARCORE")

PLUGIN_DIR=os.path.join(
    ROOT,
    "plugins"
)

ENABLED=os.path.join(
    PLUGIN_DIR,
    "enabled"
)

DISABLED=os.path.join(
    PLUGIN_DIR,
    "disabled"
)


def list_plugins():

    print("STARCORE PLUGINS")

    for path,name in [
        (ENABLED,"ENABLED"),
        (DISABLED,"DISABLED")
    ]:

        if os.path.exists(path):

            for item in os.listdir(path):

                print(
                    f"{name}: {item}"
                )



def enable(name):

    src=os.path.join(
        DISABLED,
        name
    )

    dst=os.path.join(
        ENABLED,
        name
    )


    if os.path.exists(src):

        shutil.move(
            src,
            dst
        )

        print(
            "Enabled:",
            name
        )

    else:

        print(
            "Plugin not found"
        )



def disable(name):

    src=os.path.join(
        ENABLED,
        name
    )

    dst=os.path.join(
        DISABLED,
        name
    )


    if os.path.exists(src):

        shutil.move(
            src,
            dst
        )

        print(
            "Disabled:",
            name
        )

    else:

        print(
            "Plugin not found"
        )



if __name__=="__main__":


    if len(sys.argv)<2:

        list_plugins()

        exit()


    cmd=sys.argv[1]


    if cmd=="list":

        list_plugins()


    elif cmd=="enable":

        enable(
            sys.argv[2]
        )


    elif cmd=="disable":

        disable(
            sys.argv[2]
        )



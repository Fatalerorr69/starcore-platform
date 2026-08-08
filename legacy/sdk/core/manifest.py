#!/usr/bin/env python3

import json
import os


def create_manifest(path,name,version):

    manifest={
        "name":name,
        "version":version,
        "type":"STARCORE_MODULE",
        "dependencies":[],
        "permissions":[],
        "healthcheck":"enabled"
    }


    with open(path,"w") as f:
        json.dump(manifest,f,indent=4)


if __name__=="__main__":

    create_manifest(
        os.path.expanduser(
        "~/STARCORE/runtime/sdk/example_manifest.json"),
        "example",
        "1.0"
    )

    print("MANIFEST ENGINE ONLINE")

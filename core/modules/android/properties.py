from android_cmd import getprop


PROPERTIES=[

"ro.product.model",
"ro.product.brand",
"ro.build.version.release",
"ro.build.version.sdk",
"ro.build.version.security_patch",
"ro.boot.verifiedbootstate",
"ro.boot.flash.locked",
"ro.build.fingerprint"

]


def collect():

    output={}


    for p in PROPERTIES:

        output[p]=getprop(p)


    return output



if __name__=="__main__":

    print(
        collect()
    )

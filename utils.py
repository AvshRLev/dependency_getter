from flask.wrappers import Response

def clean_version(version):
    if version == "*":
        version = "latest"
        return version
    if version[0] == "^" or version[0] == "~":
        version = version[1:] 
        return version
    if version[0] == ">":
        version = "latest"
        return version
    if version[-1] == "x":
        version = version.replace("x", "0")
        return version
    return version

def extract_deps(response):
    if response == None:
        return Response("This has returned None", 404)
    deps = {}
    devDeps = {}
    if 'dependencies' in response:
        deps = response['dependencies']
    if 'devDependencies' in response:
        devDeps = response['devDependencies']
    return {
        "deps": deps,
        "devDeps": devDeps
    }
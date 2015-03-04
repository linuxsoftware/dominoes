#---------------------------------------------------------------------------
# build webassets bundles offline
#---------------------------------------------------------------------------
import os
import sys
from pyramid.paster import bootstrap
import webassets.script


def main():
    env = setup()
    req = env['request']
    args = sys.argv[2:]
    if not args:
        args = ["build"]
    webassets.script.main(args, req.webassets_env)
    env['closer']()

def setup(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    configUri = argv[1]
    env = bootstrap(configUri)
    return env

def usage(argv):
    cmd = os.path.basename(argv[0])
    print("usage: %s <config URI>\n"
          "(example: '%s dev.ini')" % (cmd, cmd))
    sys.exit(1)

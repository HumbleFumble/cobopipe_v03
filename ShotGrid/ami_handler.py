import sys
import urllib.parse
import pprint

def main(args):
    print('main')
    # Make sure we have only one arg, the URL
    if len(args) != 1:
        return 1
    # Parse the URL:
    protocol, fullPath = args[0].split(":", 1)
    path, fullArgs = fullPath.split("?", 1)
    action = path.strip("/")
    args = fullArgs.split("&")
    params = urllib.parse.parse_qs(fullArgs)
    print(params)
    # This is where you can do something productive based on the params and the
    # action value in the URL. For now we'll just print out the contents of the
    # parsed URL.
    fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\ShotGrid\output.txt', 'w')
    fh.write(pprint.pformat((action, params)))
    fh.close()


if __name__ == '__main__':
    # print('Running :D')
    # fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\ShotGrid\output.txt', 'w+')
    # for arg in sys.argv:
    #     fh.write(arg + "\n")
    # fh.close()
    sys.exit(main(sys.argv[1:]))
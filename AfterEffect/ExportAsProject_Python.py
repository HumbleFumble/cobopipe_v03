import os.path
import sys

def run(*args):
    # print(os.path.dirname(__file__))
    # f = open(f"{os.path.dirname(__file__)}/Test.txt","w+")
    # f.close()
    return args

if __name__ == "__main__":
    print(sys.argv)
    run(sys.argv)

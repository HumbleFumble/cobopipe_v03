import os

def __main__(*args):
    os.system(r'net use p: \\dumpap3\production')
    os.system(r'net use w: \\dumpap3\WFH')
    os.system(r'net use t: \\dumpap3\tools')
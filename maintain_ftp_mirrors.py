import os
import sys
sys.path.append(os.path.dirname(__file__))
from ftpUtil import maintain_ftp_mirrors

if __name__ == '__main__':
    maintain_ftp_mirrors()
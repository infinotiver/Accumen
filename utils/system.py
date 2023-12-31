import os, sys


def restart_bot(mode):
    if mode == 1:
        os.execv(sys.executable, ["python"] + sys.argv)
    if mode == 2:
        os.system("busybox reboot")

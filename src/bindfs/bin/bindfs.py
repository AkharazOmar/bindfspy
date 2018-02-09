import os
import sys
import argparse
import logging

from contextlib import contextmanager

from fuse import FUSE
from os.path import realpath

from bindfs.bindfs import BindFs


@contextmanager
def open_dir(src):
    src_fd = os.open(src, os.O_RDONLY)
    yield src_fd
    os.close(src_fd)



def main(*args, **kwargs):
    parse = argparse.ArgumentParser(
        description="bindfspy: FIXME"
    )

    parse.add_argument("-s", "--src", type=str, required=True)
    parse.add_argument("-d", "--dst", type=str, required=True)

    args_parse = parse.parse_args()
    src = realpath(args_parse.src)
    dst = realpath(args_parse.dst)
    if src == dst:
        kwargs["nonempty"] = True


    # Open mount source for chrooting in bindfs_init
    with open_dir(src) as src_fd:
        FUSE(BindFs(src_fd), dst, *args, foreground=True, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())

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


def run_fuse(src, dst, *args, **kwargs):
    # Open mount source for chrooting in bindfs_init
    with open_dir(src) as src_fd:
        FUSE(BindFs(src_fd), dst, *args, foreground=True, **kwargs)


def main(*args, **kwargs):
    parse = argparse.ArgumentParser(
        description="bindfspy: FIXME"
    )

    parse.add_argument("-s", "--src", type=str, required=True)
    parse.add_argument("-d", "--dst", type=str, required=True)
    # foreground_parse = parse.add_mutually_exclusive_group(required=False)
    parse.add_argument("-f", "--foreground", dest="foreground", action="store_true", default=False)
    args_parse = parse.parse_args()

    src = realpath(args_parse.src)
    dst = realpath(args_parse.dst)

    if src == dst:
        kwargs["nonempty"] = True

    if (not args_parse.foreground and os.fork() == 0) or args_parse.foreground:
        run_fuse(src, dst, *args, **kwargs)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())

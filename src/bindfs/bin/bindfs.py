import os
import sys
import argparse
import logging

from pathlib import Path
from contextlib import contextmanager

from fuse import FUSE

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


def directory(dir_path, raise_error: bool=True):
    real_path = Path(dir_path).resolve()
    if not real_path.is_dir():
        if raise_error:
            raise argparse.ArgumentParser("{} must exist directory.".format(real_path.as_posix()))
        else:
            return None
    return real_path.as_posix()


def main(*args, **kwargs):
    parse = argparse.ArgumentParser(
        description="bindfspy: FIXME"
    )

    parse.add_argument(
        "-s",
        "--src",
        type=directory,
        required=True,
        help="The source directory to bind.",
    )
    parse.add_argument(
        "-d",
        "--dst",
        type=directory,
        required=True,
        help="The mount point (destination directory).",
    )
    # foreground_parse = parse.add_mutually_exclusive_group(required=False)
    parse.add_argument(
        "-f",
        "--foreground",
        dest="foreground",
        action="store_true",
        default=False,
        help="Launch process in foreground more. Default=False"
    )
    args_parse = parse.parse_args()

    src = args_parse.src
    dst = args_parse.dst

    if src == dst:
        kwargs["nonempty"] = True

    if (not args_parse.foreground and os.fork() == 0) or args_parse.foreground:
        run_fuse(src, dst, *args, **kwargs)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())

import os
import sys
import argparse
import logging

from pathlib import Path
from contextlib import contextmanager

from fuse import FUSE

from bindfs.bindfs import BindFs


class VerboseAction(argparse._StoreTrueAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, 'foreground', False) or getattr(namespace, 'console', False):
            setattr(namespace, self.dest, self.const)
        else:
            parser.error('Verbose need foreground or console')



logger = logging.getLogger(__name__)


@contextmanager
def open_dir(src: str) -> "dir_fd":
    """
    Open directory file descriptor.

    :param src: (str) the path of directory to open
    :return: directory file descriptor
    :raise: AssertionError: We the src is not directory.

    :usage example:
    >>> with open_dir("/directory/to/open") as src_fd:
    >>>     # Treatement
    >>>     pass
    """

    assert(os.path.isdir(src))
    src_fd = os.open(src, os.O_RDONLY)
    yield src_fd
    os.close(src_fd)


def run_fuse(src: str, dst: str, *args, **kwargs):
    """
    Launch fuse instance.
    :param src: (str) the path to bind
    :param dst: (str) the mount point
    :param args:
    :param kwargs:
    """
    # Open mount source for chrooting in bindfs_init
    with open_dir(src) as src_fd:
        FUSE(BindFs(src_fd), dst, *args, foreground=True, **kwargs)


def directory(dir_path: str, raise_error: bool=True) -> str:
    """
    Used by argparse for check the argument.
    :param dir_path: (str) directory to check
    :param raise_error: (bool) if True raise exception else return None when check failed.
    :return: the real path of directory if exist else None
    :raise: ArgumentParser if raise_error is True and the directory don't exist.
    """
    real_path = Path(dir_path).resolve()
    if not real_path.is_dir():
        if raise_error:
            raise argparse.ArgumentParser("{} must exist directory.".format(real_path.as_posix()))
        else:
            return None
    return real_path.as_posix()


def output_path(file_path: str, raise_error: bool=True) -> str:
    """
    Used by argparse for check the argument.
    :param file_path: (str)  file to check
    :param raise_error: (bool) if True raise exception else return None when check failed.
    :return: the real path of directory if exist else None
    :raise: ArgumentParser if raise_error is True and the directory don't exist.
    """
    real_file = Path(file_path).resolve()
    if real_file.exists():
        if not real_file.is_file():
            raise argparse.ArgumentParser("{} must be file".format(real_file))
        else:
            return real_file.as_posix()
     # else:
    try:
        real_file.touch()
        if not real_file.exists():
            raise argparse.ArgumentParser("Error when try to create output file")
    except Exception as ex:
        raise argparse.ArgumentParser("Impossible to create the log file. Reason: {}".format(ex))
    return real_file.as_posix()


def main(*args, **kwargs):
    """
    Initialise the logger and parse argument before to launch Fuse.
    :param args:
    :param kwargs:
    :return:
    """
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
    parse.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action=VerboseAction,
        default=False,
        help="Verbose mode. Required foreground or output",
    )
    parse.add_argument(
        "-o",
        "--output",
        type=output_path,
        help="Define the output log file.",
        required=False,
        default=None,
    )

    args_parse = parse.parse_args()

    src = args_parse.src
    dst = args_parse.dst

    if src == dst:
        kwargs["nonempty"] = True

    if args_parse.output or args_parse.foreground:
        level = logging.INFO
        if args_parse.verbose:
            level = logging.DEBUG

        logging.basicConfig(
            level=level,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
        )

        if args_parse.output:
            logfile = logging.FileHandler(args_parse.output)
            logfile.setLevel(level)
            logfile.setFormatter(
                logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
            )
            logging.getLogger().addHandler(logfile)

    logger.debug(
        "Launch bindfspy with the argument source={} destination={} foreground={}".format(
            src,
            dst,
            args_parse.foreground)
    )
    if (not args_parse.foreground and os.fork() == 0) or args_parse.foreground:
        run_fuse(src, dst, *args, **kwargs)


if __name__ == '__main__':
    sys.exit(main())

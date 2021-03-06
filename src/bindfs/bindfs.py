import os
import logging


from errno import EACCES
from threading import Lock

from fuse import FuseOSError, Operations

logger = logging.getLogger(__name__)


class BindFs(Operations):

    def __init__(self, root_fd):
        logger.debug("init bindfs")
        self.root_fd = root_fd
        os.fchdir(root_fd)
        self.rwlock = Lock()

    def __call__(self, op, path, *args):
        logger.debug("call: {}, path: {}".format(op, os.path.realpath("." + path)))
        return super(BindFs, self).__call__(op, "." + path, *args)

    def access(self, path, mode):
        if not os.access(path, mode):
            raise FuseOSError(EACCES)

    def create(self, path, mode, **kwargs):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        if datasync != 0:
            return os.fdatasync(fh)
        else:
            return os.fsync(fh)

    def getattr(self, path, fh=None):
        st = os.lstat(path)
        return dict(
            (key, getattr(st, key)) for key in (
                'st_atime',
                'st_ctime',
                'st_gid',
                'st_mode',
                'st_mtime',
                'st_nlink',
                'st_size',
                'st_uid'))

    getxattr = None

    def link(self, target, source):
        return os.link(source, target)

    listxattr = None

    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.read(fh, size)

    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)

    def release(self, path, fh):
        return os.close(fh)

    def rename(self, old, new):
        return os.rename(old, self.root + new)

    def statfs(self, path):
        stv = os.statvfs(path)
        return dict(
            (key, getattr(stv, key)) for key in (
                'f_bavail',
                'f_bfree',
                'f_blocks',
                'f_bsize',
                'f_favail',
                'f_ffree',
                'f_files',
                'f_flag',
                'f_frsize',
                'f_namemax')
        )

    def symlink(self, target, source):
        return os.symlink(source, target)

    def truncate(self, path, length, fh=None):
        with open(path, 'r+') as f:
            f.truncate(length)

    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)

    # Default operation. bind os.
    chmod = os.chmod
    chown = os.chown
    getxattr = None
    listxattr = None
    mkdir = os.mkdir
    mknod = os.mknod
    open = os.open
    unlink = os.unlink
    utimens = os.utime
    rmdir = os.rmdir
    readlink = os.readlink

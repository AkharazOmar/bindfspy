import unittest

from fuse import FUSE
from unittest import TestCase
from bindfs.bin.bindfs import open_dir


class TestBindFs(TestCase):
    def test_bindfs(self):
        from bindfs.bindfs import BindFs

        with open_dir("/home/omar/Téléchargements"):
            FUSE(BindFs("/home/omar/Téléchargements"))


if __name__ == '__main__':
    unittest.main()
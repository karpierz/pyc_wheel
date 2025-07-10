# Copyright (c) 2019 Adam Karpierz
# SPDX-License-Identifier: MIT

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import platform

import pyc_wheel
from pyc_wheel import main

here = Path(__file__).resolve().parent
data_dir = here/"data"

py_implementation = platform.python_implementation()
py_version = "".join(platform.python_version_tuple()[0:2])


class MainTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.is_cpython = py_implementation.lower() == "cpython"
        cls.data_dir   = Path(tempfile.mkdtemp(prefix="pyc_wheel_"))
        cls.copydir(data_dir, cls.data_dir, dirs_exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.rmdir(cls.data_dir)

    def test_simple(self):
        whl_file = self.data_dir/"renumerate-1.3.5-py3-none-any.whl"
        main([str(whl_file), "--quiet"])
        self.assertTrue(whl_file.exists())

    def test_with_backup(self):
        whl_file = self.data_dir/"slownie-1.4.5-py3-none-any.whl"
        whl_file_bak = whl_file.with_suffix(whl_file.suffix + ".bak")
        main([str(whl_file), "--with_backup"])
        self.assertTrue(whl_file.exists())
        self.assertTrue(whl_file_bak.exists())

    def test_exclude(self):
        whl_file = self.data_dir/"let3-1.2.3-py3-none-any.whl"
        main([str(whl_file), "--exclude", r"_le?\.py"])
        self.assertTrue(whl_file.exists())

    def test_exclude_all(self):
        whl_file = self.data_dir/"let3-1.2.3-py3-none-any_exclude_all.whl"
        main([str(whl_file), "--exclude", r".+"])
        self.assertTrue(whl_file.exists())

    def test_without_py(self):
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any_without_py.whl"
        main([str(whl_file)])
        self.assertTrue(whl_file.exists())

    @unittest.skipUnless(py_implementation.lower() in ("cpython", "pypy"),
                         "Only for CPython or PyPy")
    def test_rename(self):
        py_tag_prefix = "cp" if self.is_cpython else "pp"
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any.whl"
        whl_file_renamed = self.data_dir/(f"annotate-1.2.4-{py_tag_prefix}{py_version}-"
                                          "none-any.whl")
        main([str(whl_file), "--rename"])
        self.assertFalse(whl_file.exists())
        self.assertTrue(whl_file_renamed.exists())

    @unittest.skipUnless(py_implementation.lower() in ("cpython", "pypy"),
                         "Only for CPython or PyPy")
    def test_symlink(self):
        py_tag_prefix = "cp" if self.is_cpython else "pp"
        whl_file = self.data_dir/"pkg_about-1.3.7-py3-none-any.whl"
        whl_file_renamed = self.data_dir/(f"pkg_about-1.3.7-{py_tag_prefix}{py_version}-"
                                          "none-any.whl")
        main([str(whl_file), "--symlink"])
        self.assertTrue(whl_file.exists())
        self.assertTrue(whl_file_renamed.exists())
        self.assertTrue(whl_file.is_symlink())
        self.assertTrue(whl_file.samefile(whl_file_renamed))

    @unittest.skipUnless(py_implementation.lower() in ("cpython", "pypy"),
                         "Only for CPython or PyPy")
    def test_with_tag(self):
        py_tag_prefix = "cp" if self.is_cpython else "pp"
        py_ver_prefix = "cp" if self.is_cpython else "pypy"
        py_ver_suffix = ""   if self.is_cpython else "_pp73"
        whl_file = self.data_dir/(f"crc_ct-1.4.3-{py_tag_prefix}{py_version}-"
                                  f"{py_ver_prefix}{py_version}{py_ver_suffix}-win_amd64.whl")
        main([str(whl_file)])
        self.assertTrue(whl_file.exists())

    def test_invalid_suffix(self):
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any.invalid_suffix"
        with self.assertRaisesRegex(TypeError, "File to convert must be .+"):
            main([str(whl_file)])

    def test_not_compilable(self):
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any_not_compilable.whl"
        with self.assertRaisesRegex(RuntimeError, "Error compiling Python sources in .+"):
            main([str(whl_file)])

    def test_without_tag(self):
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any_without_tag.whl"
        with self.assertRaisesRegex(RuntimeError, "No tags present in .+"):
            main([str(whl_file)])

    def test_unknown_tag(self):
        whl_file = self.data_dir/"annotate-1.2.4-py3-none-any_unknown_tag.whl"
        with self.assertRaisesRegex(RuntimeError, "Cannot convert wheel with .+"):
            main([str(whl_file)])

    # Utilities

    @classmethod  # pragma: no cover
    def mkdir(cls, path: Path, mode=0o777, parents=False, exist_ok=True):
        return path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    @classmethod  # pragma: no cover
    def rmdir(cls, path: Path, *, ignore_errors=False, onerror=None):
        if not path.exists(): return
        shutil.rmtree(str(path), ignore_errors=ignore_errors,
                      onerror=onerror or cls.__remove_readonly)

    @staticmethod  # pragma: no cover
    def __remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    @classmethod  # pragma: no cover
    def copydir(cls, src: Path, dst: Path, *, symlinks=False, ignore=None,
                copy_function=None, ignore_dangling_symlinks=False, dirs_exist_ok=False):
        return Path(shutil.copytree(str(src), str(dst), symlinks=symlinks, ignore=ignore,
                                    copy_function=copy_function or shutil.copy2,
                                    ignore_dangling_symlinks=ignore_dangling_symlinks,
                                    dirs_exist_ok=dirs_exist_ok))

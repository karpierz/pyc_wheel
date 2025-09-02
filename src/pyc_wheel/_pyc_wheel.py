# Copyright (c) 2016 Grant Patten
# Copyright (c) 2019 Adam Karpierz
# SPDX-License-Identifier: MIT

"""Compile all py files in a wheel to pyc files."""

import platform
import sys
import os
import setuptools  # noqa: F401 # needed because distutils
import distutils
import re
import stat
import shutil
import tempfile
import glob
import compileall
import zipfile
import hashlib
import csv
import base64
from datetime import datetime
from pathlib import Path
import logging

__all__ = ('convert_wheel', 'main')


HASH_ALGORITHM = hashlib.sha256

py_implementation = platform.python_implementation()
# append major & minor version as these versions may change
# the magic number indicating the pyc file version
py_major_version = platform.python_version_tuple()[0]
py_minor_version = platform.python_version_tuple()[1]


def create_python_tag() -> str:
    # The Python tag indicates the implementation and version required by a distribution, see:
    # https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#python-tag
    if py_implementation.lower() == "cpython":
        py_impl_abbrev = "cp"
    elif py_implementation.lower() == "pypy":  # pragma: no cover
        py_impl_abbrev = "pp"
    else:
        raise NotImplementedError("Python implementation currently not supported!")
    return f"{py_impl_abbrev}{py_major_version}{py_minor_version}"


def create_pyc_whl_path(source_whl: Path) -> Path:
    source_whl_name = source_whl.name
    # {version}(-{build tag})?-{python tag}-{abitag}-{platform tag} -> list
    tags = source_whl_name.split("-")
    tags[-3] = create_python_tag()
    pyc_whl_name = "-".join(tags)
    pyc_whl = (source_whl.parent/pyc_whl_name).with_suffix(".whl")
    return pyc_whl


def convert_wheel(whl_file: Path, *,
                  exclude: re.Pattern[str] | str | None = None,
                  with_backup: bool = False, rename: str | bool = False,
                  quiet: bool = False, optimize: int = 0) -> Path:
    """Generate a new whl with only pyc files."""

    if whl_file.suffix != ".whl":
        raise TypeError("File to convert must be a *.whl")

    if rename == "symlink" and not hasattr(os, "symlink"):
        raise NotImplementedError("symlinks are not supported on this platform")

    if not isinstance(rename, bool) and rename != "symlink":  # pragma: no cover
        raise ValueError("rename must be a boolean or 'symlink'")

    if isinstance(exclude, str): exclude = re.compile(exclude) if exclude else None

    dist_info = "-".join(whl_file.stem.split("-")[:-3])

    whl_path = Path(tempfile.mkdtemp())
    try:
        # Extract our zip file temporarily
        with zipfile.ZipFile(str(whl_file), "r") as whl_zip:
            whl_zip.extractall(whl_path)
            members = [member for member in whl_zip.infolist()
                       if member.is_dir() or not member.filename.endswith(".py")]

        # Compile all py files
        if not compileall.compile_dir(whl_path, rx=exclude,
                                      ddir=f"<{dist_info}>",
                                      quiet=int(quiet), force=True, legacy=True,
                                      optimize=optimize):
            raise RuntimeError(f"Error compiling Python sources in wheel {whl_file.name}")

        # Remove all original py files
        for py_file in whl_path.glob("**/*.py"):
            if py_file.is_file():  # pragma: no branch
                if exclude is None or not exclude.search(str(py_file)):
                    if not quiet: print(f"Deleting py file: {py_file}")
                    py_file.chmod(stat.S_IWUSR)
                    py_file.unlink()
        # To be sure
        for root, dirs, files in os.walk(whl_path):
            for fname in files:
                if fname.endswith(".py"):  # pragma: no cover
                    py_file = Path(root)/fname
                    if exclude is None or not exclude.search(str(py_file)):
                        if not quiet: print(f"Removing file: {py_file}")
                        py_file.chmod(stat.S_IWUSR)
                        py_file.unlink()

        for member in members:
            file_path = whl_path/member.filename
            timestamp = datetime(*member.date_time).timestamp()
            try:
                os.utime(file_path, (timestamp, timestamp))
            except Exception:  # pragma: no cover
                pass  # ignore errors
            permission_bits = (member.external_attr >> 16) & 0o777
            try:
                os.chmod(file_path, permission_bits)
            except Exception:  # pragma: no cover
                pass  # ignore errors

        dist_info_path = whl_path/f"{dist_info}.dist-info"
        rewrite_dist_info(dist_info_path, exclude=exclude)

        # Rezip the file with the new version info
        whl_file_zip = whl_path.with_suffix(".zip")
        if whl_file_zip.exists(): whl_file_zip.unlink()
        shutil.make_archive(str(whl_path), "zip", root_dir=str(whl_path))
        if with_backup:
            whl_file.replace(whl_file.with_suffix(whl_file.suffix + ".bak"))
        if rename:
            pyc_whl_path = create_pyc_whl_path(whl_file)
            shutil.move(whl_file_zip, pyc_whl_path)
            if whl_file != pyc_whl_path:  # pragma: no branch
                whl_file.unlink(missing_ok=True)
                if rename == "symlink":
                    whl_file.symlink_to(pyc_whl_path)
                if not quiet: print("Renamed wheel: "
                                    f"{whl_file} -> {pyc_whl_path}")
            whl_file = pyc_whl_path
        else:
            shutil.move(whl_file_zip, whl_file)
        return whl_file
    finally:
        # Clean up original directory
        shutil.rmtree(str(whl_path), ignore_errors=True)


def rewrite_dist_info(dist_info_path: Path, *,
                      exclude: re.Pattern[str] | str | None = None) -> None:
    """Rewrite the record file with pyc files instead of py files."""

    whl_path = dist_info_path.resolve().parent

    if isinstance(exclude, str): exclude = re.compile(exclude) if exclude else None

    # Rewrite the record file with pyc files instead of py files.

    record_path = dist_info_path/"RECORD"
    record_path.chmod(stat.S_IWUSR | stat.S_IRUSR)

    record_data = []
    with record_path.open("r") as record:
        for file_dest, file_hash, file_len in csv.reader(record):
            if file_dest.endswith(".py"):
                # Do not keep py files, replace with pyc files
                if exclude is None or not exclude.search(file_dest):
                    fpath_dest = Path(file_dest)
                    # pyc_fname = "{}.{}-{}{}.pyc".format(
                    #             fpath_dest.stem,
                    #             platform.python_implementation().lower(),
                    #             sys.version_info.major,
                    #             sys.version_info.minor)
                    # pyc_file = fpath_dest.parent/"__pycache__"/pyc_fname
                    pyc_file = fpath_dest.with_suffix(".pyc")
                    file_dest = str(pyc_file)

                    pyc_path = whl_path/pyc_file
                    with pyc_path.open("rb") as f:
                        data = f.read()
                    hash_obj = HASH_ALGORITHM(data)
                    file_hash = f"{hash_obj.name}={_b64encode(hash_obj.digest())}"
                    file_len  = str(len(data))
            record_data.append((file_dest, file_hash, file_len))

    with record_path.open("w", newline="\n") as record:
        csv.writer(record,
                   lineterminator="\n").writerows(sorted(set(record_data)))

    # Rewrite the wheel info file.

    wheel_path = dist_info_path/"WHEEL"
    wheel_path.chmod(stat.S_IWUSR | stat.S_IRUSR)

    with wheel_path.open("r") as wheel:
        wheel_data = wheel.readlines()

    tags = [tag for line in wheel_data
            if line.startswith("Tag: ") and (tag := line.split(" ")[1].strip())]
    if not tags:
        raise RuntimeError(f"No tags present in {wheel_path.parent.name}/{wheel_path.name}; "
                           "cannot determine target wheel filename")
    # Reassemble the tag for the wheel file
    pyc_tag = None
    for tag in tags:
        tag_components = tag.split("-")
        python_tag = tag_components[0]
        if python_tag == f"py{py_major_version}":
            tag_components[0] = create_python_tag()
            pyc_tag = "-".join(tag_components)
            break
        if (python_tag == f"cp{py_major_version}{py_minor_version}"
           and py_implementation.lower() == "cpython"):
            tag_components[0] = create_python_tag()
            pyc_tag = "-".join(tag_components)
            break
        if (python_tag == f"pp{py_major_version}{py_minor_version}"  # pragma: no cover
           and py_implementation.lower() == "pypy"):
            tag_components[0] = create_python_tag()
            pyc_tag = "-".join(tag_components)
            break

    if pyc_tag is None:
        raise RuntimeError("Cannot convert wheel with the used interpreter.")

    with wheel_path.open("w") as wheel:
        for line in wheel_data:
            if line.startswith("Tag: "):
                wheel.write(f"Tag: {pyc_tag}")
            else:
                wheel.write(line)


def _get_platform() -> str:  # pragma: no cover # not used for now
    """Return our platform name 'win32', 'linux_x86_64'"""
    get_platform = distutils.util.get_platform  # type: ignore[attr-defined]
    result: str = get_platform().replace(".", "_").replace("-", "_")
    if result == "linux_x86_64" and sys.maxsize == 2147483647:
        # pip pull request #3497
        result = "linux_i686"
    return result


def _b64encode(data: bytes) -> str:
    """urlsafe_b64encode without padding"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def main(argv: list[str] = sys.argv[1:]) -> int:
    """Compile all py files in a wheel"""
    from argparse import ArgumentParser
    app_name = __package__
    parser = ArgumentParser(prog=f"python -m {app_name}", description=main.__doc__)
    parser.add_argument("whl_file",
                        help="Path (can contain wildcards) to whl(s) to convert")
    parser.add_argument("--exclude", default=None,
                        help="skip files matching the regular expression; "
                             "the regexp is searched for in the full path "
                             "of each file considered for compilation")
    parser.add_argument("--with_backup", "--with-backup", default=False, action="store_true",
                        help="Indicates whether the backup will be created.")
    rename_group = parser.add_mutually_exclusive_group()
    rename_group.add_argument("--rename", default=False, action="store_true",
                              help="Rename the wheel to python version.")
    if hasattr(os, "symlink"):  # pragma: no branch
        rename_group.add_argument("--symlink", dest="rename", action="store_const",
                                  const="symlink",
                                  help="Rename the wheel to python version and symlink "
                                       "old name to new.")
    parser.add_argument("--optimize", default=0, type=int, choices=[0, 1, 2],
                        help="Specifies the optimization level of the compiler."
                             "Explicit levels are 0 (no optimization; __debug__ is true),"
                             "1 (asserts are removed, __debug__ is false) or"
                             "2 (docstrings are removed too)")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Indicates whether the filenames and other "
                             "conversion information will be printed to "
                             "the standard output.")
    parser.add_argument("--log", type=str, default="warning",
                        choices=["critical", "error", "warning", "info", "debug"],
                        help="Provide logging level. "
                             "Example --log debug, default='warning'")
    args = parser.parse_args(argv)
    # logging config
    logging.basicConfig(format="[%(levelname)s]:%(message)s",
                        level=getattr(logging, args.log.upper()))

    for whl_file in glob.iglob(args.whl_file):
        convert_wheel(Path(whl_file), exclude=args.exclude,
                      with_backup=args.with_backup, rename=args.rename,
                      quiet=args.quiet, optimize=args.optimize)
    return 0

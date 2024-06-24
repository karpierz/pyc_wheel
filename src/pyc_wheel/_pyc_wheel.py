# Copyright (c) 2016 Grant Patten
# Copyright (c) 2019-2021 Adam Karpierz
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

"""Compile all py files in a wheel to pyc files."""
import pathlib
import platform
import sys
import os
import setuptools
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

__all__ = ('convert_wheel', 'main')


HASH_ALGORITHM = hashlib.sha256


def create_python_tag() -> str:
    # The Python tag indicates the implementation and version required by a distribution,
    # see https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#python-tag
    python_impl = platform.python_implementation()
    if python_impl == "PyPy":
        python_impl_abbrev = "pp"
    elif python_impl == "CPython":
        python_impl_abbrev = "cp"
    else:
        raise NotImplementedError("Python implementation currently not supported!")

    # append major & minor version as these versions may change the magic number indicating the pyc file version
    py_major_version = platform.python_version_tuple()[0]
    py_minor_version = platform.python_version_tuple()[1]

    return f"{python_impl_abbrev}{py_major_version}{py_minor_version}"


def create_pyc_whl_path(source_whl: pathlib.Path) -> pathlib.Path:
    source_whl_name = source_whl.name
    tags = source_whl_name.split('-')  # {version}(-{build tag})?-{python tag}-{abitag}-{platform tag} -> list
    tags[-3] = create_python_tag()
    pyc_whl_name = '-'.join(tags)
    pyc_whl = (source_whl.parent / pyc_whl_name).with_suffix('.whl')
    return pyc_whl


def convert_wheel(whl_file: Path, *, exclude=None, with_backup=False, quiet=False, optimize=0):
    """Generate a new whl with only pyc files."""

    if whl_file.suffix != ".whl":
        raise TypeError("File to convert must be a *.whl")

    if exclude: exclude = re.compile(exclude)

    dist_info = "-".join(whl_file.stem.split("-")[:-3])

    whl_dir  = tempfile.mkdtemp()
    whl_path = Path(whl_dir)

    try:
        # Extract our zip file temporarily
        with zipfile.ZipFile(str(whl_file), "r") as whl_zip:
            whl_zip.extractall(whl_dir)
            members = [member for member in whl_zip.infolist()
                       if member.is_dir() or not member.filename.endswith(".py")]

        # Compile all py files
        if not compileall.compile_dir(whl_dir, rx=exclude,
                                      ddir="<{}>".format(dist_info),
                                      quiet=int(quiet), force=True, legacy=True, optimize=optimize):
            raise RuntimeError("Error compiling Python sources in wheel "
                               "{!s}".format(whl_file.name))

        # Remove all original py files
        for py_file in whl_path.glob("**/*.py"):
            if py_file.is_file():
                if exclude is None or not exclude.search(str(py_file)):
                    if not quiet: print("Deleting py file: {!s}".format(py_file))
                    py_file.chmod(stat.S_IWUSR)
                    py_file.unlink()

        for root, dirs, files in os.walk(whl_dir):
            for fname in files:
                if fname.endswith(".py"):
                    py_file = Path(root)/fname
                    if exclude is None or not exclude.search(str(py_file)):
                        if not quiet: print("Removing file: {!s}".format(py_file))
                        py_file.chmod(stat.S_IWUSR)
                        py_file.unlink()

        for member in members:
            file_path = whl_path/member.filename
            timestamp = datetime(*member.date_time).timestamp()
            try:
                os.utime(str(file_path), (timestamp, timestamp))
            except Exception:
                pass  # ignore errors

        dist_info_path = whl_path/"{}.dist-info".format(dist_info)
        rewrite_dist_info(dist_info_path, exclude=exclude)

        # Rezip the file with the new version info
        whl_file_zip = whl_path.with_suffix(".zip")
        if whl_file_zip.exists(): whl_file_zip.unlink()
        shutil.make_archive(whl_dir, "zip", root_dir=whl_dir)
        if with_backup:
            whl_file.replace(whl_file.with_suffix(whl_file.suffix + ".bak"))
        shutil.move(str(whl_file_zip), str(create_pyc_whl_path(whl_file)))
    finally:
        # Clean up original directory
        shutil.rmtree(whl_dir, ignore_errors=True)


def rewrite_dist_info(dist_info_path: Path, *, exclude=None):
    """Rewrite the record file with pyc files instead of py files."""

    whl_path = dist_info_path.resolve().parent

    # Rewrite the record file with pyc files instead of py files.

    record_path = dist_info_path/"RECORD"
    record_path.chmod(stat.S_IWUSR | stat.S_IRUSR)

    record_data = []
    with record_path.open("r") as record:
        for file_dest, file_hash, file_len in csv.reader(record):
            if file_dest.endswith(".py"):
                # Do not keep py files, replace with pyc files
                if exclude is None or not exclude.search(file_dest):
                    file_dest = Path(file_dest)
                    # import platform
                    # pyc_fname = "{}.{}-{}{}.pyc".format(
                    #             file_dest.stem,
                    #             platform.python_implementation().lower(),
                    #             sys.version_info.major,
                    #             sys.version_info.minor)
                    # pyc_file = file_dest.parent/"__pycache__"/pyc_fname
                    pyc_file = file_dest.with_suffix(".pyc")
                    file_dest = str(pyc_file)

                    pyc_path = whl_path/pyc_file
                    with pyc_path.open("rb") as f:
                        data = f.read()
                    file_hash = HASH_ALGORITHM(data)
                    file_hash = "{}={}".format(file_hash.name,
                                               _b64encode(file_hash.digest()))
                    file_len  = len(data)
            record_data.append((file_dest, file_hash, file_len))

    with record_path.open("w", newline="\n") as record:
        csv.writer(record,
                   lineterminator="\n").writerows(sorted(set(record_data)))

    # Rewrite the wheel info file.

    wheel_path = dist_info_path/"WHEEL"
    wheel_path.chmod(stat.S_IWUSR | stat.S_IRUSR)

    with wheel_path.open("r") as wheel:
        wheel_data = wheel.readlines()

    tags = [line.split(" ")[1].strip()
            for line in wheel_data if line.startswith("Tag: ")]
    if not tags:
        raise RuntimeError("No tags present in {}/{}; cannot determine target"
                           " wheel filename".format(wheel_path.parent.name,
                                                    wheel_path.name))
    # Reassemble the tag for the wheel file
    pyc_tag = None
    for tag in tags:
        tag_components = tag.split("-")
        python_tag = tag_components[0]
        py_major_version = platform.python_version_tuple()[0]
        if python_tag == f"py{py_major_version}":
            tag_components[0] = create_python_tag()
            pyc_tag = '-'.join(tag_components)
            break

    if pyc_tag is None:
        raise RuntimeError("Cannot convert wheel with the used interpreter.")

    with wheel_path.open("w") as wheel:
        for line in wheel_data:
            if line.startswith("Tag: "):
                wheel.write(f"Tag: {pyc_tag}")
            else:
                wheel.write(line)


def _get_platform():
    """Return our platform name 'win32', 'linux_x86_64'"""
    result = distutils.util.get_platform().replace(".", "_").replace("-", "_")
    if result == "linux_x86_64" and sys.maxsize == 2147483647:
        # pip pull request #3497
        result = "linux_i686"
    return result


def _b64encode(data):
    """urlsafe_b64encode without padding"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def main(argv=sys.argv[1:]):
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Compile all py files in a wheel")
    parser.add_argument("whl_file",
                        help="Path (can contain wildcards) to whl(s) to convert")
    parser.add_argument("--exclude", default=None,
                        help="skip files matching the regular expression; "
                             "the regexp is searched for in the full path "
                             "of each file considered for compilation")
    parser.add_argument("--with_backup", default=False, action="store_true",
                        help="Indicates whether the backup will be created.")
    parser.add_argument("--quiet", default=False, action="store_true",
                        help="Indicates whether the filenames and other "
                             "conversion information will be printed to "
                             "the standard output.")
    parser.add_argument("--optimize", default=0, type=int, choices=[0, 1, 2],
                        help="Specifies the optimization level of the compiler."
                             "Explicit levels are 0 (no optimization; __debug__ is true),"
                             "1 (asserts are removed, __debug__ is false) or"
                             "2 (docstrings are removed too)")
    args = parser.parse_args(argv)
    for whl_file in glob.iglob(args.whl_file):
        convert_wheel(Path(whl_file), exclude=args.exclude,
                      with_backup=args.with_backup, quiet=args.quiet, optimize=args.optimize)

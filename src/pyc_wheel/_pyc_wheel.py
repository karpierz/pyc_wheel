# Copyright (c) 2016 Grant Patten
# Copyright (c) 2019-2019 Adam Karpierz
# Licensed under the MIT License
# https://opensource.org/licenses/MIT

"""Compile all py files in a wheel to pyc files."""

import sys
import os
import platform
import shutil
import compileall
import zipfile
import hashlib
import csv
from base64 import urlsafe_b64encode
from pathlib import Path

__all__ = ('convert_wheel',)


HASH_TYPE = "sha256"


def convert_wheel(whl_file: Path, *, with_backup=False):
    """Generate a new whl with only pyc files.

    This whl will append .compiled to the version information.
    """

    if whl_file.suffix != ".whl":
        raise TypeError("File to convert must be a *.whl")

    whl_path = whl_file.with_suffix("")
    whl_dir = str(whl_path)

    # Clean up leftover files
    shutil.rmtree(whl_dir, ignore_errors=True)

    # Extract our zip file temporarily
    with zipfile.ZipFile(str(whl_file), "r") as whl_zip:
        whl_zip.extractall(whl_dir)

    try:
        # Replace all py files with pyc files
        compileall.compile_dir(whl_dir)

        # Remove all original py files
        for py_file in whl_path.glob("**/*.py"):
            print("Deleting py file: {}".format(py_file))
            py_file.unlink()

        for root, dirs, files in os.walk(whl_dir):
            for f in files:
                if f.endswith(".py"):
                    py_file = Path(root)/f
                    print("Removing file: {}".format(py_file))
                    py_file.unlink()

        # Update the record data
        dist_info_name = "{}.dist-info".format("-".join(whl_dir.split("-")[:-3]))
        dist_info_path = whl_path/dist_info_name
        rewrite_dist_info(dist_info_path)

        # Rezip the file with the new version info
        if with_backup:
            whl_file.replace(whl_file.with_suffix(whl_file.suffix + ".bak"))
        whl_file_zip = whl_file.with_suffix(".zip")
        if whl_file_zip.exists(): whl_file_zip.unlink()
        shutil.make_archive(whl_dir, "zip", root_dir=whl_dir)
        whl_file_zip.replace(whl_file)
    finally:
        # Clean up original directory
        shutil.rmtree(whl_dir)


def rewrite_dist_info(dist_info_path: Path):
    """Rewrite the record file with pyc files instead of py files."""

    whl_path = dist_info_path.resolve().parent
    record_path = dist_info_path/"RECORD"

    record_data = []
    with record_path.open("r") as record:
        for file_dest, file_hash, file_len in csv.reader(record):
            if file_dest.endswith(".py"):
                # Do not keep py files, replace with pyc files
                file_dest = Path(file_dest)
                pyc_fname = "{}.{}-{}{}.pyc".format(
                                file_dest.stem,
                                platform.python_implementation().lower(),
                                sys.version_info.major,
                                sys.version_info.minor)
                pyc_file = file_dest.parent/"__pycache__"/pyc_fname
                file_dest = str(pyc_file)

                file_hash = hashlib.new(HASH_TYPE)
                file_len = 0
                pyc_path = whl_path/pyc_file
                with pyc_path.open("rb") as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        file_hash.update(data)
                        file_len += len(data)

                hash_str = file_hash.digest()
                hash_str = urlsafe_b64encode(file_hash.digest())
                hash_str = urlsafe_b64encode(file_hash.digest()).rstrip(b"=")
                file_hash = "{}={}".format(HASH_TYPE, hash_str)
            record_data.append((file_dest, file_hash, file_len))

    with record_path.open("w", newline="\n") as record:
        csv.writer(record,
                   lineterminator="\n").writerows(sorted(set(record_data)))


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Compile all py files in a wheel")
    parser.add_argument("whl_file", help="Path to whl to convert")
    parser.add_argument("--with_backup", default=False, action="store_true",
                        help="Indicates whether the backup will be created.")
    args = parser.parse_args(args)
    convert_wheel(Path(args.whl_file), with_backup=args.with_backup)

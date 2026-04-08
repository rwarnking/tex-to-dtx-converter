import pathmagic  # noqa isort:skip

import filecmp
import os
import sys
from pathlib import Path

import pytest
from core.converter import Converter
from meta_information import MetaInformation

# https://stackoverflow.com/questions/404744/
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app path
    APP_PATH = Path(os.path.dirname(sys.executable))
else:
    APP_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


def get_test_folders():
    test_dir = Path(os.path.normpath(APP_PATH / ".." / "tests"))
    return [
        Path(f.path) for f in os.scandir(test_dir) if f.is_dir() and f.name.startswith("test_case")
    ]


@pytest.mark.parametrize("folder", get_test_folders())
def test_converter(folder):
    rsc_dir = folder
    tgt_dir = rsc_dir / "results"

    meta_info = MetaInformation()
    meta_info.set_dirs(rsc_dir, tgt_dir)

    converter = Converter(meta_info)
    converter.execute()

    output = tgt_dir / f"{folder.name.replace('_', '')}.dtx"
    expected = tgt_dir / "expected.dtx"

    assert output.exists(), f"{folder.name.replace('_', '')}: output file missing"
    assert expected.exists(), f"{folder.name}: expected file missing"

    assert filecmp.cmp(output, expected, shallow=False), f"{folder.name}: files differ"

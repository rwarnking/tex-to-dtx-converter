from pathlib import Path

from core.converter import Converter
from meta_information import MetaInformation


class CliApp:
    def __init__(self, src_dir: Path, tgt_dir: Path):
        self.meta_info = MetaInformation()
        self.meta_info.set_dirs(src_dir, tgt_dir)

    def run(self):
        converter = Converter(self.meta_info)
        converter.execute()
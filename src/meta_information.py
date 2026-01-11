from pathlib import Path


class MetaInformation:
    """Collection class for all kinds of metainformation and program settings."""

    def __init__(self):
        """Setup all meta information."""
        self.finished = True

        self.cur_file_count = 0
        self.max_file_count = 0

    def reset(self):
        self.finished = True
        self.cur_file_count = 0
        self.max_file_count = 0

    def incr_file_count(self):
        self.cur_file_count += 1

    def set_max_file_count(self, count: int):
        self.max_file_count = count

    def get_cur_file_count(self) -> int:
        return self.cur_file_count

    def get_max_file_count(self) -> int:
        return self.max_file_count

    def set_dirs(self, src_dir: Path, tgt_dir: Path):
        """Set the source and target directories."""
        self.src_dir = src_dir
        self.tgt_dir = tgt_dir

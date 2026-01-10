from converter.tex_dtx import TexDtxConverter
from pathlib import Path


class Converter:
    def __init__(self, meta_info):
        self.meta_info = meta_info
        self.texdtx_conv = TexDtxConverter()

    def execute(self):
        src_dir = Path(self.meta_info.src_dir.get())

        self.meta_info.set_max_file_count(len(list(src_dir.iterdir())))

        parsed_tex = {}
        for file_dir in list(src_dir.iterdir()):
            ext = file_dir.suffix

            if ext == ".tex":
                section_name = file_dir.stem.split("_")[1]
                parsed_tex[section_name] = self.texdtx_conv.parse_tex(file_dir)
            else:
                print(f"Unknown file type for file {file_dir.stem}.")

            self.meta_info.incr_file_count()

        # Save all data to one dtx
        res_dtx = self.texdtx_conv.tex_to_dtx(src_dir/"docu", parsed_tex)
        # TODO
        self._save_to_dir(f"glmatrix.dtx", res_dtx)

        self.meta_info.finished = True

    def _save_to_dir(self, filename, content):
        tgt_dir = Path(self.meta_info.tgt_dir.get())
        print(tgt_dir / filename)
        # print(content.encode('ascii', 'ignore'))

        with open(tgt_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)

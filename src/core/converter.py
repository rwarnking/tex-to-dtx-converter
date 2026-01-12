import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import TypedDict

from meta_information import MetaInformation

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app path
    TEMPLATE_PATH = Path(os.path.dirname(sys.executable)) / "tex_templates"
else:
    TEMPLATE_PATH = Path(os.path.dirname(os.path.abspath(__file__))) / "tex_templates"


class ParsedObject(TypedDict):
    o_type: None | str
    o_content: list[str]
    o_category: Path


class ParsedCommand(TypedDict):
    name: str
    oarg: tuple[str, str]
    oarg_default: None | str
    args: list[tuple[str, str]]
    desc: list[str]
    todos: list[str]
    errors: list[str]
    equation: list[str]
    example: list[str]
    private: bool


class Converter:
    """
    https://www.texdev.net/2009/10/06/a-model-dtx-file/
    """

    def __init__(self, meta_info: MetaInformation):
        self.meta_info = meta_info

    def execute(self):
        rsc_dir: Path = self.meta_info.rsc_dir

        self.meta_info.set_max_file_count(len(list(rsc_dir.iterdir())))

        self._load_package_metainfo(rsc_dir)

        parsed_tex: dict[str, list[ParsedObject]] = {}
        for file_dir in list(rsc_dir.iterdir()):
            ext = file_dir.suffix

            if ext == ".tex":
                section_name = file_dir.stem.split("_")[1]
                parsed_tex[section_name] = self._parse_tex(file_dir)
            else:
                print(f"Unknown file type for file {file_dir.stem}.")

            self.meta_info.incr_file_count()

        # Save all data to one dtx
        res_dtx = self._tex_to_dtx(rsc_dir / "docu", parsed_tex)
        # TODO
        self._save_to_dir(f"{self.pkg_meta['pkg_name']}.dtx", res_dtx)

        self.meta_info.finished = True

    def _save_to_dir(self, filename: str, content: str):
        tgt_dir = self.meta_info.tgt_dir
        print(tgt_dir / filename)

        with open(tgt_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)

    def _load_package_metainfo(self, rsc_dir: Path):
        # default setup
        self.pkg_meta: dict[str, str | float] = {
            "pkg_name": "SamplePackage",
            "pkg_description": "TODO",
            "pkg_author": "Sample author",
            "pkg_author_email": "example@email.com",
            "pkg_date": date.today().strftime("%Y/%m/%d"),
            "pkg_version": 1.0,
            "pkg_info_text": "Info text",
        }

        pkginfo_file_path = rsc_dir / "package_config.txt"
        # Load file if it exists, otherwise use default
        if pkginfo_file_path.exists():
            with pkginfo_file_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key == "pkg_date" and value == "today":
                            self.pkg_meta[key] = date.today().strftime("%Y/%m/%d")
                        else:
                            self.pkg_meta[key] = value

    def _parse_tex(self, file_dir: Path) -> list[ParsedObject]:
        tex_objects: list[ParsedObject] = []
        with open(file_dir, encoding="utf-8") as f:
            cur_object: ParsedObject = {"o_type": None, "o_content": [], "o_category": file_dir}

            lines = f.readlines()
            for line in lines:
                if line.startswith("\\newcommand"):
                    cur_object["o_type"] = "command"
                elif line.startswith("}"):
                    cur_object["o_content"].append(line)
                    tex_objects.append(cur_object)
                    cur_object = {
                        "o_type": None,
                        "o_content": [],
                        "o_category": file_dir,
                    }
                # If the line starts with % then it must be comment
                elif (
                    line.startswith("% ")
                    and cur_object["o_type"] != "command"
                    and cur_object["o_type"] != "header"
                ):
                    cur_object["o_type"] = "comment"
                elif line.startswith("%%") and cur_object["o_type"] == "header":
                    cur_object["o_type"] = None
                elif line.startswith("%%") and cur_object["o_type"] != "command":
                    cur_object["o_type"] = "header"
                # If the line is empty and the current object type is comment - reset
                elif line.rstrip() == "" and cur_object["o_type"] == "comment":
                    cur_object = {
                        "o_type": None,
                        "o_content": [],
                        "o_category": file_dir,
                    }
                elif cur_object["o_type"] is None and line.rstrip() != "":
                    print(f"Unprocessed line: {line}.")

                if cur_object["o_type"] == "command" or cur_object["o_type"] == "comment":
                    cur_object["o_content"].append(line)

        return tex_objects

    def _tex_to_dtx(self, rsc_dir: Path, parsed_tex: dict[str, list[ParsedObject]]) -> str:
        docu_output = ""
        impl_output = ""
        impl_output += "%    \\begin{macrocode}\n"
        impl_output += "%<*package>\n"
        impl_output += "%    \\end{macrocode}\n\n"

        output = ""
        output += self._add_header(rsc_dir)

        for key, value in parsed_tex.items():
            cur_docu_output = ""
            # cur_docu_output = f"% \\subsection{{{key}}}\n"
            # docu_output += "% \\etocsettocstyle{}{}\n"
            # docu_output += "% \\etocsetnexttocdepth{3}\n"
            # docu_output += "% \\localtableofcontents*\n"

            docu_table = "% \\begin{center}\n"
            docu_table += "% \\begin{tabularx}{\\textwidth}{l l l} \\hline\n"
            docu_table += "% \\textbf{Command} & \\textbf{Arguments} & "
            docu_table += "\\textbf{Default Argument} \\\\ \\hline\n"
            impl_table = "% \\begin{center}\n"
            impl_table += "% \\begin{tabularx}{\\textwidth}{l l l} \\hline\n"
            impl_table += "% \\textbf{Command} & \\textbf{Arguments} & "
            impl_table += "\\textbf{Default Argument} \\\\ \\hline\n"

            cur_impl_output = ""
            # cur_impl_output = f"% \\subsection{{{key}}}\n"
            # impl_output += "% \\etocsettocstyle{}{}\n"
            # impl_output += "% \\etocsetnexttocdepth{3}\n"
            # impl_output += "% \\localtableofcontents*\n"

            for obj in value:
                if obj["o_type"] == "command":
                    obj_docu, obj_impl, cmd = self._parse_command(obj)
                    if not cmd["private"]:
                        cur_docu_output += obj_docu
                        cur_impl_output += obj_impl

                        if cmd["oarg_default"]:
                            args_str = f"\\oarg{{{cmd["oarg"][0]}}}, "
                        else:
                            args_str = ""
                        args_str += ", ".join([f"\\marg{{{e[0]}}}" for e in cmd["args"]])
                        docu_table += f"% \\ref{{macro:{cmd['name']}}} & "
                        docu_table += f"{args_str} & "
                        # docu_table += f"{args_str} & Another macro description.\\\\\n"
                        impl_table += f"% \\ref{{macro:{cmd['name']}}} & "
                        impl_table += f"{args_str} & "
                        # impl_table += f"{args_str} & Another macro description."
                        if cmd["oarg_default"]:
                            impl_table += f"{cmd['oarg_default']}\\\\\n"
                            docu_table += f"{cmd['oarg_default']}\\\\\n"
                        else:
                            impl_table += "\\\\\n"
                            docu_table += "\\\\\n"

            docu_table += "% \\end{tabularx}\n"
            docu_table += "% \\end{center}\n"
            impl_table += "% \\end{tabularx}\n"
            impl_table += "% \\end{center}\n\n"
            docu_output += f"% \\subsection{{{key}}}\n" + docu_table + cur_docu_output
            impl_output += f"% \\subsection{{{key}}}\n" + impl_table + cur_impl_output

        impl_output += "%    \\begin{macrocode}\n"
        impl_output += "%</package>\n"
        impl_output += "%    \\end{macrocode}\n"

        output += "% \\section{Macro Documentation}\n"
        output += docu_output
        # output += "% \\StopEventually{\\PrintIndex}\n\n"
        output += "\n"
        output += "% \\section{Implementation}\n\n"
        output += impl_output

        return output

    def _add_header(self, rsc_dir: Path) -> str:
        header = ""

        header += self._fill_template(TEMPLATE_PATH / Path("01_head.tex"))
        header += self._fill_template(TEMPLATE_PATH / Path("02_preamble_template.tex"))
        header += self._fill_template(TEMPLATE_PATH / Path("03_postamble_template.tex"))
        header += self._fill_template(TEMPLATE_PATH / Path("04_generate_template.tex"))

        # Load packages (no template)
        with open(rsc_dir / "packages_and_settings.tex", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                header += line
        header += "\n"

        header += self._fill_template(TEMPLATE_PATH / Path("05_predocument.tex"))
        header += self._fill_template(TEMPLATE_PATH / Path("06_document_template.tex"))

        introduction = ""
        with open(rsc_dir / "introduction.tex", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                introduction += f"% {line}"
        introduction += "\n"

        return header + introduction

    def _parse_command(self, command_obj) -> tuple[str, str, ParsedCommand]:
        obj_docu = ""
        obj_impl = ""

        command: ParsedCommand = {
            "name": "unknown",
            "oarg": ("", ""),
            "oarg_default": None,
            "args": [],
            "desc": [],
            "todos": [],
            "errors": [],
            "equation": [],
            "example": [],
            "private": False,
        }
        found_command_start = False
        for line in command_obj["o_content"]:
            if line.startswith("% Private"):
                command["private"] = True
            elif line.startswith("\\newcommand"):
                match = re.search(r"\\newcommand\\(\w+)", line)
                if match:
                    # print(match.group(1))
                    command["name"] = match.group(1)
                found_command_start = True
                # command["oarg"] = line.count("[") > 1

                # pattern = re.compile(r"\[\d+\](?:\[([^\]]+)\])?")
                match = re.search(r"\[\d+\](?:\[([^\]]+)\])?", line)
                if match:
                    command["oarg_default"] = match.group(1)

                # print(pattern.search("text[3][Result]").group(1))
                # print(pattern.search("text[3]").group(1))
            elif line.startswith("% #"):
                match = re.search(r"#\d+\s+([^,]+),\s*(.+)$", line)
                if match:
                    command["args"].append((match.group(1), match.group(2)))
            elif line.startswith("% TODO") and not found_command_start:
                command["todos"].append(line)
            elif line.startswith("% Equation") and not found_command_start:
                command["equation"].append(line)
            elif line.startswith("% Example") and not found_command_start:
                command["example"].append(line)
            elif line.startswith("% Error") and not found_command_start:
                command["errors"].append(line)
            elif line.startswith("% ") and not found_command_start:
                command["desc"].append(line)

        if command["oarg_default"]:
            command["oarg"] = command["args"][0]
            command["args"] = command["args"][1:]

        # Construct command documentation string
        obj_docu += (
            f"\n% \\setlabel{{\\textbackslash {command['name']}}}{{macro:{command['name']}}}\n"
        )
        obj_docu += f"% \\DescribeMacro{{{command['name']}}}\n"

        if command["oarg_default"]:
            obj_docu += f"% \\oarg{{{command['oarg'][0]}}}"
        else:
            obj_docu += "% "
        obj_docu += "".join([f"\\marg{{{e[0]}}}" for e in command["args"]])
        obj_docu += "\\\\\n"

        if command["oarg_default"]:
            obj_docu += f"% \\oarg{{{command['oarg'][0]}}}: {command['oarg'][1]}, "
            obj_docu += f"default: {command['oarg_default']}\\\\\n"
        for arg in command["args"]:
            obj_docu += f"% \\marg{{{arg[0]}}}: {arg[1]}\\\\\n"
        obj_docu += "\n"
        obj_docu += "".join(command["desc"])
        obj_docu += "\n"
        if len(command["equation"]) > 0:
            obj_docu += self._add_equation_box(command["equation"])
        if len(command["example"]) > 0:
            obj_docu += self._add_example_box(command["example"])
        if len(command["errors"]) > 0:
            obj_docu += self._add_warning_box(command["errors"])

        # Filter documentation text for param numbers (e.g. #2)
        def replace_match(match):
            n = int(match.group(1))
            if n - 1 >= len(command["args"]):
                print(f"Replacement error: list not long enough {command['name']}")
                return f"param {n}"
            return command["args"][n - 1][0]

        obj_docu = re.sub(r"#(\d+)", replace_match, obj_docu)

        # Construct command implementation string
        obj_impl += f"% \\begin{{macro}}{{\\{command['name']}}}\n"
        obj_impl += "%    \\begin{macrocode}\n"

        obj_impl += "".join(command_obj["o_content"])

        obj_impl += "%    \\end{macrocode}\n"
        obj_impl += "% \\end{macro}\n\n"

        return obj_docu, obj_impl, command

    def _fill_template(self, file_path: Path) -> str:
        # Read the entire file into one string
        if file_path.exists():
            result: str = file_path.read_text(encoding="utf-8")

            for key, value in self.pkg_meta.items():
                result = result.replace(f"<{key.upper()}>", f"{value}")
            return result
        else:
            print(f"File {file_path} does not exist.")
            return ""

    # TODO these tree can be merged into one generic function
    def _add_example_box(self, example_strs: list[str]) -> str:
        example = "% \\begin{examplebox}\n"

        for line in example_strs[:-1]:
            _line = line.split("% Example:")[1].strip()
            example += f"%   {_line}\\\\\n"
        _line = example_strs[-1].split("% Example:")[1].strip()
        example += f"%   {_line}\n"

        example += "% \\end{examplebox}\n"

        return example

    def _add_equation_box(self, equation_strs: list[str]) -> str:
        equation = "% \\begin{equationbox}\n"

        for line in equation_strs[:-1]:
            _line = line.split("% Equation:")[1].strip()
            equation += f"%   {_line}\\\\\n"
        _line = equation_strs[-1].split("% Equation:")[1].strip()
        equation += f"%   {_line}\n"

        equation += "% \\end{equationbox}\n"

        return equation

    def _add_warning_box(self, warning_strs: list[str]) -> str:
        warning = "% \\begin{warningbox}\n"

        for line in warning_strs[:-1]:
            _line = line.split("% Error:")[1].strip()
            warning += f"%   {_line}\\\\\n"
        _line = warning_strs[-1].split("% Error:")[1].strip()
        warning += f"%   {_line}\n"

        warning += "% \\end{warningbox}\n"

        return warning

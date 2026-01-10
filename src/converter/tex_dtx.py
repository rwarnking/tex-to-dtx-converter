import re


# https://www.texdev.net/2009/10/06/a-model-dtx-file/
class TexDtxConverter:
    def __init__(self):
        # TODO this is stupid
        self.last_elem_was_text = False

    def parse_tex(self, file_dir):
        tex_objects = []
        with open(file_dir, encoding="utf-8") as f:
            out_content = ""
            cur_object = {
                "o_type": None,
                "o_content": [],
                "o_category": file_dir
            }

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
                        "o_category": file_dir
                    }
                # If the line starts with % then it must be comment
                elif line.startswith("% ") and cur_object["o_type"] != "command" and cur_object["o_type"] != "header":
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
                        "o_category": file_dir
                    }
                elif cur_object["o_type"] == None and line.rstrip() != "":
                    print(f"Unprocessed line: {line}.")

                if (cur_object["o_type"] == "command" or 
                    cur_object["o_type"] == "comment"
                ):
                    cur_object["o_content"].append(line)

        return tex_objects

    def tex_to_dtx(self, src_dir, parsed_tex):
        docu_output = ""
        impl_output = ""

        output = ""

        output += self._add_header(src_dir)

        for key, value in parsed_tex.items():
            cur_docu_output = f""
            # cur_docu_output = f"% \\subsection{{{key}}}\n"
            # docu_output += "% \\etocsettocstyle{}{}\n"
            # docu_output += "% \\etocsetnexttocdepth{3}\n"
            # docu_output += "% \\localtableofcontents*\n"

            docu_table = "% \\begin{center}\n"
            docu_table += "% \\begin{tabularx}{\\textwidth}{l p{3cm} l} \\hline\n"
            docu_table += "% \\textbf{Command} & \\textbf{Arguments} & \\textbf{Short Description} \\\\ \\hline\n"
            impl_table = "% \\begin{center}\n"
            impl_table += "% \\begin{tabularx}{\\textwidth}{l p{3cm} l} \\hline\n"
            impl_table += "% \\textbf{Command} & \\textbf{Arguments} & \\textbf{Short Description} \\\\ \\hline\n"
            
            cur_impl_output = f""
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
                        if cmd["oarg"]:
                            args_str = f"\\oarg{{{cmd['oarg'][0]}}}\n"
                        else:
                            args_str = ""
                        args_str += ", ".join([f"\\marg{{{e[0]}}}" for e in cmd["args"]])
                        docu_table += f"% \\ref{{macro:{cmd['name']}}} & {args_str} & Another macro description.\\\\\n"
                        impl_table += f"% \\ref{{macro:{cmd['name']}}} & {args_str} & Another macro description.\\\\\n"

            docu_table += "% \\end{tabularx}\n"
            docu_table += "% \\end{center}\n"
            impl_table += "% \\end{tabularx}\n"
            impl_table += "% \\end{center}\n"
            docu_output += f"% \\subsection{{{key}}}\n" + docu_table + cur_docu_output
            impl_output += f"% \\subsection{{{key}}}\n" + impl_table + cur_impl_output

        output += "% \\section{Macro Documentation}\n"
        output += docu_output
        output += "% \\StopEventually{\\PrintIndex}\n\n"
        output += "% \\section{Implementation}\n"
        output += impl_output

        return output

    def _add_header(self, src_dir):
        pkg_name = "glmatrix"
        pkg_author = "Rene Warnking"
        pkg_date = "2025/12/15"

        header = """% \\iffalse meta-comment
%<*internal>
\\iffalse
%</internal>
%<*readme>
Some README information here :-)
%</readme>
\\NeedsTeXFormat{LaTeX2e}
"""
        header += f"\\ProvidesPackage{{{pkg_name}}}[2025/12/15 v0.1 Object abstraction]\n"

        with open(src_dir/"header.tex", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                header += line
        header += "\n"

        header += f"""
\\begin{{document}}
    \\title{{The \\textsf{{{pkg_name}}} Package}}
    \\author{{{pkg_author}}}
    \\date{{{pkg_date}}}
    \\maketitle

    \\tableofcontents

    \\DocInput{{{pkg_name}.dtx}}
\\end{{document}}
%</driver>
% \\fi
"""

        introduction = ""
        with open(src_dir/"introduction.tex", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                introduction += f"% {line}"
        introduction += "\n"

        return header + introduction

    def _parse_command(self, command_obj):
        obj_docu = ""
        obj_impl = ""

        command = {
            "name": "unknown",
            "oarg": None,
            "oarg_default": None,
            "args": [],
            "desc": [],
            "todos": [],
            "errors": [],
            "equation": None,
            "example": "",
            "private": False
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

                # print(pattern.search("text[3][Result]").group(1))  # Result
                # print(pattern.search("text[3]").group(1))          # None
            elif line.startswith("% #"):
                match = re.search(r"#\d+\s+([^,]+),\s*(.+)$", line)
                if match:
                    command["args"].append((
                        match.group(1),
                        match.group(2)
                    ))
            elif line.startswith("% TODO") and not found_command_start:
                command["todos"].append(line)
            elif line.startswith("% Equation") and not found_command_start:
                command["equation"] = line.split("% Equation:")[1]
            elif line.startswith("% Example") and not found_command_start:
                command["example"] += line.split("% Example:")[1] + "\n"
            elif line.startswith("% Error") and not found_command_start:
                command["errors"].append(line.split("% Error:")[1])
            elif line.startswith("% ") and not found_command_start:
                command["desc"].append(line)

        # if command["oarg_default"] and len(command["args"]) < 1:
        #     print(command["name"])

        if command["oarg_default"]:
            command["oarg"] = command["args"][0]
            command["args"] = command["args"][1:]

        # Construct command documentation string
        obj_docu += f"% \\setlabel{{\\textbackslash {command['name']}}}{{macro:{command['name']}}}\n"
        obj_docu += f"% \\DescribeMacro{{{command['name']}}}\n"
        if command["oarg"]:
            obj_docu += f"\\oarg{{{command['oarg'][0]}}}\n"
        obj_docu += "".join([f"\\marg{{{e[0]}}}" for e in command["args"]])
        obj_docu += "\n\n"
        if command["oarg"]:
            obj_docu += f"\\oarg{{{command['oarg'][0]}}}: {command['oarg'][1]}, default: {command['oarg_default']}\n\n"
        for arg in command["args"]:
            obj_docu += f"\\marg{{{arg[0]}}}: {arg[1]}\n\n"
        obj_docu += "\n"
        obj_docu += "".join(command["desc"])
        obj_docu += "\n"
        if command["equation"]:
            obj_docu += f"\\begin{{equationbox}}Equation: {command['equation']}\\end{{equationbox}}"
        if command["example"]:
            obj_docu += f"\\begin{{examplebox}}{command['example']}\\end{{examplebox}}"
        for error in command["errors"]:
            obj_docu += f"\\begin{{warningbox}}Error: {error}\\end{{warningbox}}"

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

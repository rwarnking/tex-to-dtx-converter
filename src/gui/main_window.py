import threading
from idlelib.tooltip import Hovertip
from pathlib import Path
from tkinter import HORIZONTAL, Button, Label, StringVar, Tk, filedialog, messagebox
from tkinter.ttk import Progressbar, Separator

# own imports
from core.converter import Converter
from gui.helper import center_window
from gui.settings import PAD_X, PAD_Y
from gui.tooltips import TooltipDict
from meta_information import MetaInformation


class GuiApp:
    def __init__(self, rsc_dir: Path, tgt_dir: Path):
        self.window = Tk()
        self.window.title("Tex to Dtx Converter")

        self.meta_info = MetaInformation()

        self.row_idx = 0

        self.init_resource_folder(rsc_dir, tgt_dir)
        separator = Separator(self.window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_progressindicator()

        self.btn_run = Button(self.window, text="Convert", command=lambda: self.run())
        self.btn_run.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=10)
        Hovertip(self.btn_run, TooltipDict["btn_run"])

        center_window(self.window)
        self.window.mainloop()

    def row(self):
        """Keep track of the row the GUI is in."""
        self.row_idx += 1
        return self.row_idx - 1

    def run(self):
        """Main application loop that starts the sorting thread on keypress."""
        if not self.meta_info.finished:
            messagebox.showinfo(message="Conversion is already happening.", title="Error")
            return

        if self.meta_info.rsc_dir == "" or self.meta_info.tgt_dir == "":
            messagebox.showinfo(message="No folder selected.", title="Error")
            return

        self.meta_info.finished = False
        converter = Converter(self.meta_info)

        self.lbl_progstate.config(text="Conversion in progress.")
        self.new_thread = threading.Thread(target=converter.execute)
        self.new_thread.start()
        self.window.after(50, lambda: self.listen_for_result())

    def listen_for_result(self):
        """Update the GUI on the number of files processed and how many are still left."""
        # TODO what was this for
        tmp = self.meta_info.finished

        count_cur_file = self.meta_info.get_cur_file_count()
        count_max_file = self.meta_info.get_max_file_count()

        self.file_progress["value"] = count_cur_file
        self.file_progress["maximum"] = count_max_file
        self.file_progress.update()

        self.lbl_mile_prog.config(text=f"Finished file {count_cur_file} of {count_max_file}.")

        if not self.meta_info.finished and not tmp:
            self.window.after(50, lambda: self.listen_for_result())
        else:
            self.lbl_progstate.config(text="Finished all files.")
            self.meta_info.reset()

    ###############################################################################################
    # Initialization functions
    ###############################################################################################
    def init_resource_folder(self, rsc_dir: Path, tgt_dir: Path):
        """Add GUI elemtens for source and target directory."""

        def browse_button(dir: StringVar):
            filename = filedialog.askdirectory(initialdir=dir.get())
            if filename != "":
                dir.set(filename)

        self.sv_rsc_dir = StringVar()
        self.sv_rsc_dir.set(str(rsc_dir))
        self.sv_tgt_dir = StringVar()
        self.sv_tgt_dir.set(str(tgt_dir))
        self.meta_info.set_dirs(rsc_dir, tgt_dir)

        # Source directory
        lbl1 = Label(self.window, text="Source directory:")
        lbl1.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_rsc_dir = Label(self.window, textvariable=self.sv_rsc_dir)
        lbl_rsc_dir.grid(
            row=self.row_idx,
            column=1,
            columnspan=1,
            padx=PAD_X,
            pady=PAD_Y,
            sticky="EW",
        )
        btn_src = Button(
            self.window,
            text="Browse",
            command=lambda: browse_button(self.sv_rsc_dir),
        )
        btn_src.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_src, TooltipDict["btn_src"])

        # Target directory
        lbl2 = Label(self.window, text="Target directory:")
        lbl2.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tgt_dir = Label(self.window, textvariable=self.sv_tgt_dir)
        lbl_tgt_dir.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        btn_tgt = Button(
            self.window,
            text="Browse",
            command=lambda: browse_button(self.sv_tgt_dir),
        )
        btn_tgt.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_tgt, TooltipDict["btn_tgt"])

    def init_progressindicator(self):
        """Add GUI progressbar and corresponding label."""
        # Update to get the correct width for the progressbar
        self.window.update()
        w_width = self.window.winfo_width()
        # Progress bar widget
        self.file_progress = Progressbar(
            self.window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.file_progress["value"] = 0
        self.file_progress.update()
        self.file_progress.grid(row=self.row(), columnspan=3, sticky="EW", padx=PAD_X, pady=PAD_Y)
        self.lbl_mile_prog = Label(self.window, text="")
        self.lbl_mile_prog.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X, pady=PAD_Y)

        # Progress label
        self.lbl_progstate = Label(self.window, text="Program is not yet running!")
        self.lbl_progstate.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X, pady=PAD_Y)

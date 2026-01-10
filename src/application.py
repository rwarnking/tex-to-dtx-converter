import os
import sys
import threading
from idlelib.tooltip import Hovertip
from tkinter import (
    HORIZONTAL,
    Button,
    Label,
    StringVar,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Progressbar, Separator

# own imports
from gui.helper import center_window
from gui.settings import PAD_X, PAD_Y
from gui.tooltips import TooltipDict
from converter.converter import Converter
from meta_information import MetaInformation

# https://stackoverflow.com/questions/404744/
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app path
    APP_PATH = os.path.dirname(sys.executable)
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))


class MainApp:
    def __init__(self, window: Tk):

        self.meta_info = MetaInformation()

        self.row_idx = 0

        self.init_resource_folder(window)
        separator = Separator(window, orient="horizontal")
        separator.grid(row=self.row(), column=0, columnspan=3, padx=PAD_X, pady=PAD_Y, sticky="EW")
        self.init_progressindicator(window)

        self.btn_run = Button(window, text="Convert", command=lambda: self.run(window))
        self.btn_run.grid(row=self.row_idx, column=0, columnspan=3, padx=PAD_X, pady=10)
        Hovertip(self.btn_run, TooltipDict["btn_run"])

        center_window(window)

    def row(self):
        """Keep track of the row the GUI is in."""
        self.row_idx += 1
        return self.row_idx - 1

    def run(self, window: Tk):
        """Main application loop that starts the sorting thread on keypress."""
        if not self.meta_info.finished:
            messagebox.showinfo(message="Conversion is already happening.", title="Error")
            return

        if self.meta_info.src_dir.get() == "" or self.meta_info.tgt_dir.get() == "":
            messagebox.showinfo(message="No folder selected.", title="Error")
            return

        self.meta_info.finished = False
        converter = Converter(self.meta_info)

        self.lbl_progstate.config(text="Conversion in progress.")
        self.new_thread = threading.Thread(target=converter.execute)
        self.new_thread.start()
        window.after(50, lambda: self.listen_for_result(window))

    def listen_for_result(self, window: Tk):
        """Update the GUI on the number of files processed and how many are still left."""
        tmp = self.meta_info.finished

        count_cur_file = self.meta_info.get_cur_file_count()
        count_max_file = self.meta_info.get_max_file_count()

        self.file_progress["value"] = count_cur_file
        self.file_progress["maximum"] = count_max_file
        self.file_progress.update()

        self.lbl_mile_prog.config(text=f"Finished file {count_cur_file} of {count_max_file}.")

        if not self.meta_info.finished and not tmp:
            window.after(50, lambda: self.listen_for_result(window))
        else:
            self.lbl_progstate.config(text="Finished all files.")
            self.meta_info.reset()

    ###############################################################################################
    # Initialization functions
    ###############################################################################################
    def init_resource_folder(self, window: Tk):
        """Add GUI elemtens for source and target directory."""

        def browse_button(dir: StringVar):
            filename = filedialog.askdirectory(initialdir=dir.get())
            if filename != "":
                dir.set(filename)

        self.meta_info.set_dirs(APP_PATH + "/../test-data/source", APP_PATH + "/../test-data/target")

        # Source directory
        lbl1 = Label(window, text="Source directory:")
        lbl1.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_src_dir = Label(window, textvariable=self.meta_info.src_dir)
        lbl_src_dir.grid(
            row=self.row_idx, column=1, columnspan=1, padx=PAD_X, pady=PAD_Y, sticky="EW"
        )
        btn_src = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.src_dir),
        )
        btn_src.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_src, TooltipDict["btn_src"])

        # Target directory
        lbl2 = Label(window, text="Target directory:")
        lbl2.grid(row=self.row_idx, column=0, padx=PAD_X, pady=PAD_Y, sticky="EW")
        lbl_tgt_dir = Label(window, textvariable=self.meta_info.tgt_dir)
        lbl_tgt_dir.grid(row=self.row_idx, column=1, padx=PAD_X, pady=PAD_Y, sticky="EW")
        btn_tgt = Button(
            window,
            text="Browse",
            command=lambda: browse_button(self.meta_info.tgt_dir),
        )
        btn_tgt.grid(row=self.row(), column=2, padx=PAD_X, pady=PAD_Y, sticky="EW")
        Hovertip(btn_tgt, TooltipDict["btn_tgt"])

    def init_progressindicator(self, window: Tk):
        """Add GUI progressbar and corresponding label."""
        # Update to get the correct width for the progressbar
        window.update()
        w_width = window.winfo_width()
        # Progress bar widget
        self.file_progress = Progressbar(
            window, orient=HORIZONTAL, length=w_width, mode="determinate"
        )
        self.file_progress["value"] = 0
        self.file_progress.update()
        self.file_progress.grid(
            row=self.row(), columnspan=3, sticky="EW", padx=PAD_X, pady=PAD_Y
        )
        self.lbl_mile_prog = Label(window, text="")
        self.lbl_mile_prog.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X, pady=PAD_Y)

        # Progress label
        self.lbl_progstate = Label(window, text="Program is not yet running!")
        self.lbl_progstate.grid(row=self.row(), columnspan=3, sticky="E", padx=PAD_X, pady=PAD_Y)


###################################################################################################
# Main
###################################################################################################
if __name__ == "__main__":
    window = Tk()
    # window.title("Tex to Dtx Converter")
    # main_app = MainApp(window)
    # window.mainloop()

    meta_info = MetaInformation()
    meta_info.set_dirs(APP_PATH + "/../test-data/source", APP_PATH + "/../test-data/target")

    converter = Converter(meta_info)
    converter.execute()
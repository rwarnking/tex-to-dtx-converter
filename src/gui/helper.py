from tkinter import Tk, Toplevel
from typing import Union


def center_window(window: Union[Toplevel, Tk]):
    """Centers the given window on the screen."""
    window.update()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Calculates the x for the window to be in the center
    window_x = int((window.winfo_screenwidth() / 2) - (window_width / 2))
    # Calculates the y for the window to be in the center
    window_y = int((window.winfo_screenheight() / 2) - (window_height / 2))

    # Creates a geometric string argument
    window_geometry = (
        str(window_width) + "x" + str(window_height) + "+" + str(window_x) + "+" + str(window_y)
    )
    # Sets the geometry accordingly
    window.geometry(window_geometry)
    # Override again such that automatic window resizing works
    # https://stackoverflow.com/questions/50955987/auto-resize-tkinter-window-to-fit-all-widgets
    window.geometry("")

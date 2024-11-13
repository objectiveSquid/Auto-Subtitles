from tkinter import font as tk_font
from PIL import Image, ImageTk
import tkinter.ttk as ttk
import tkinter as tk


def seticon(root: tk.Wm, path: str) -> None:
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)

    root.wm_iconphoto(False, image)  # type: ignore


def set_font_size(widget: tk.Text, new_size: int) -> None:
    current_font = tk_font.Font(font=widget["font"])
    widget.configure(font=(current_font.actual()["family"], new_size))


def combobox_ignore_input(widget: ttk.Combobox) -> None:
    widget.bind("<Key>", lambda event: "break")
    widget.bind("<BackSpace>", lambda event: "break")
    widget.bind("<Delete>", lambda event: "break")

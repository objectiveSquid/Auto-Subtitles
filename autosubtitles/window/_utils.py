from tkinter import font as tk_font
from PIL import Image, ImageTk
import tkinter as tk


def seticon(root: tk.Wm, path: str) -> None:
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)

    root.wm_iconphoto(False, image)  # type: ignore


def set_font_size(widget: tk.Text, new_size: int) -> None:
    current_font = tk_font.Font(font=widget["font"])
    widget.configure(font=(current_font.actual()["family"], new_size))

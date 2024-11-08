from PIL import Image, ImageTk
import tkinter as tk
import threading
import time
import cv2


def seticon(root: tk.Wm, path: str) -> None:
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)

    root.wm_iconphoto(False, image)  # type: ignore


def replace_options(
    option_menu: tk.OptionMenu, variable: tk.StringVar, new_options: list[str]
):
    option_menu["menu"].delete(0, "end")

    for option in new_options:
        option_menu["menu"].add_command(
            label=option, command=lambda value=option: variable.set(value)
        )

    variable.set(new_options[0])

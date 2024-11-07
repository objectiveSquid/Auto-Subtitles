from __future__ import annotations

from model.model import (
    find_model_info_by_name,
    download_model,
    scrape_models,
    ModelInfo,
)
from misc.path import create_models_path, resourcepath, models_path
from generator.subtitle_generator import SubtitleGenerator
from ._utils import seticon
from .misc import _BG_GREY

import tkinter.messagebox as tk_messagebox
import tkinter.ttk as ttk
import tkinter as tk


class StartWindow:
    def __init__(self) -> None:
        self.lines = 0
        self.generator = None
        scrape_models()
        create_models_path()

        self.window = tk.Toplevel(background=_BG_GREY)
        self.window.wm_geometry("300x200")

        tk_messagebox.showinfo(
            "Select first model",
            "You currently have no models downloaded, you will need to choose one now.",
        )

        self.window.wm_title("Choose first model")
        seticon(self.window, resourcepath("subtitles.png"))

        tk.Label(
            self.window,
            background=_BG_GREY,
            foreground="#FFFFFF",
            text="Select model",
        ).pack(fill=tk.X)

        self.selected_model_category = tk.StringVar(
            self.window, value=list(scrape_models().keys())[0]
        )
        category_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model_category,
            values=list(scrape_models().keys()),
        )
        category_select.bind(
            "<KeyRelease>", lambda event: self.__validate_combobox(category_select)
        )
        category_select.bind(
            "<<ComboboxSelected>>",
            lambda event: self.__set_model_category(self.selected_model_category),
        )
        category_select.pack()

        self.selected_model = tk.StringVar(
            self.window,
            value=scrape_models()[self.selected_model_category.get()][0].name,
        )
        self.model_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model,
            values=[
                modelinfo.name
                for modelinfo in scrape_models()[self.selected_model_category.get()]
            ],
        )
        self.model_select.pack()

        # exit button
        tk.Button(
            self.window,
            text="Select model",
            font=("Arial", 8),
            command=self.close,
        ).place(
            relx=self.window.winfo_width() * 0.5,
            rely=self.window.winfo_width() * 0.9,
            anchor=tk.S,
        )

    def __validate_combobox(self, combobox: ttk.Combobox) -> bool:
        return combobox.get() not in combobox["values"]

    def __set_model_category(self, category: tk.StringVar | str) -> None:
        if isinstance(category, tk.StringVar):
            category = category.get()

        self.model_select["values"] = [
            modelinfo.name for modelinfo in scrape_models()[category]
        ]
        self.selected_model.set(self.model_select["values"][0])

    def close(self) -> None:
        self.window.wm_withdraw()

        modelinfo: ModelInfo = find_model_info_by_name(scrape_models(), self.selected_model.get())  # type: ignore

        download_model(self.window, modelinfo.link)

        # i will commit a holocaust on the python type system
        self.generator = SubtitleGenerator(
            f"{models_path}/{self.selected_model.get()}", modelinfo
        )

        self.window.destroy()

from __future__ import annotations

from model.model import (
    find_model_info_by_name,
    download_model,
    get_available_models,
    ModelInfo,
)
from misc.path import create_models_path, resourcepath, MODELS_PATH
from generator.subtitle_generator import SubtitleGenerator
from ._utils import seticon
from .misc import BACKGROUND_GREY

from .utils_extern import normalize_window_size
import tkinter.messagebox as tk_messagebox
import tkinter.ttk as ttk
import tkinter as tk


class StartWindow:
    def __init__(self) -> None:
        self.lines = 0
        self.generator = None
        get_available_models()
        create_models_path()

        self.window = tk.Toplevel(background=BACKGROUND_GREY)
        self.window.wm_geometry(
            normalize_window_size(self.window, (300, 200, None, None))
        )

        tk_messagebox.showinfo(
            "Select first model",
            "You currently have no models downloaded, you will need to choose one now.",
        )

        self.window.wm_title("Choose first model")
        seticon(self.window, resourcepath("subtitles.png"))

        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            text="Select model",
        ).pack(fill=tk.X)

        self.selected_model_category = tk.StringVar(
            self.window, value=list(get_available_models().keys())[0]
        )
        category_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model_category,
            values=list(get_available_models().keys()),
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
            value=get_available_models()[self.selected_model_category.get()][0].name,
        )
        self.model_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model,
            values=[
                modelinfo.name
                for modelinfo in get_available_models()[
                    self.selected_model_category.get()
                ]
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
            modelinfo.name for modelinfo in get_available_models()[category]
        ]
        self.selected_model.set(self.model_select["values"][0])

    def close(self) -> None:
        self.window.wm_withdraw()

        modelinfo: ModelInfo = find_model_info_by_name(get_available_models(), self.selected_model.get())  # type: ignore

        download_model(self.window, modelinfo.link)

        # i will commit a holocaust on the python type system
        self.generator = SubtitleGenerator(
            f"{MODELS_PATH}/{self.selected_model.get()}", modelinfo
        )

        self.window.destroy()

from __future__ import annotations

from model.model import (
    get_downloaded_models_info,
    find_model_info_by_name,
    get_downloaded_models,
    download_model,
    get_available_models,
    ModelInfo,
)
from misc.path import (
    write_previous_model_file,
    create_models_path,
    resourcepath,
    models_path,
)
from generator.subtitle_generator import SubtitleGenerator
from .misc import _BUTTON_GREY, _BUTTON_RED, _BG_GREY
from ._utils import seticon

import PIL.Image as Image, PIL.ImageTk as ImageTk
from typing import Callable, Literal
import tkinter.ttk as ttk
import tkinter as tk
import os


class SettingsWindow:
    def __init__(
        self,
        root: tk.Misc,
        current_modelinfo: ModelInfo,
        exit_callback: Callable[[], None],
    ) -> None:
        self.lines = 0
        get_available_models()
        create_models_path()

        self.parent = root
        self.window = tk.Toplevel(self.parent, background=_BG_GREY)
        self.window.wm_geometry("400x600")

        self.current_modelinfo = current_modelinfo

        self.window.wm_title("Auto Subtitles Settings")
        seticon(self.window, resourcepath("settings.png"))

        tk.Label(
            self.window,
            background=_BG_GREY,
            foreground="#FFFFFF",
            text="Select model",
        ).pack(fill=tk.X)

        self.selected_model_category = tk.StringVar(
            self.window, value=current_modelinfo.category
        )
        category_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model_category,
            values=list(get_available_models().keys()),
        )
        # disallow typing
        category_select.bind("<Key>", lambda event: "break")
        category_select.bind("<BackSpace>", lambda event: "break")
        category_select.bind("<Delete>", lambda event: "break")
        category_select.bind(
            "<<ComboboxSelected>>",
            lambda event: self.__set_model_category(self.selected_model_category),
        )
        category_select.pack()

        self.selected_model = tk.StringVar(
            self.window,
            value=current_modelinfo.name,
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
        # disallow typing
        category_select.bind("<Key>", lambda event: "break")
        category_select.bind("<BackSpace>", lambda event: "break")
        category_select.bind("<Delete>", lambda event: "break")
        self.model_select.bind(
            "<<ComboboxSelected>>",
            lambda event: self.__check_model_download(self.selected_model),
        )
        self.model_select.pack()

        self.download_model_warning = tk.Label(
            self.window, background=_BG_GREY, foreground="#FFFFFF", font=("Arial", 10)
        )
        self.download_model_warning.pack()

        # exit button
        tk.Button(
            self.window, text="Close settings", font=("Arial", 8), command=exit_callback
        ).place(
            relx=self.window.winfo_width() * 0.9,
            rely=self.window.winfo_width() * 0.9,
            anchor=tk.SE,
        )

        self.__check_model_download(self.selected_model)

    def __check_model_download(self, modelname: tk.StringVar | str) -> None:
        if isinstance(modelname, tk.StringVar):
            modelname = modelname.get()

        if modelname in get_downloaded_models():
            self.download_model_warning.configure(text="")
        elif modelname not in get_downloaded_models():
            self.download_model_warning.configure(
                text=f"Model needs to be downloaded ({find_model_info_by_name(modelname).size})"  # type: ignore
            )

    def __set_model_category(self, category: tk.StringVar | str) -> None:
        if isinstance(category, tk.StringVar):
            category = category.get()

        self.model_select["values"] = [
            modelinfo.name for modelinfo in get_available_models()[category]
        ]
        category_model_infos = get_downloaded_models_info(sort=True, category=category)
        if len(category_model_infos) > 0:
            self.selected_model.set(category_model_infos[0].name)  # type: ignore
        else:
            self.selected_model.set(self.model_select["values"][0])

        self.__check_model_download(self.selected_model)

    def close(self) -> SubtitleGenerator | None:
        self.window.wm_withdraw()

        modelinfo: ModelInfo = find_model_info_by_name(self.selected_model.get())  # type: ignore

        if self.selected_model.get() not in get_downloaded_models():
            download_model(self.window, modelinfo.link)

        write_previous_model_file(modelinfo.name)

        return SubtitleGenerator(
            f"{models_path}/{self.selected_model.get()}", modelinfo
        )


class SubtitleWindow:
    def __init__(
        self,
        width: int,
        height: int,
        subtitle_generator: SubtitleGenerator,
    ) -> None:
        self.subtitle_generator = subtitle_generator
        self.anti_garbage_collection_list = []
        self.left_buttons = 0
        self.right_buttons = 0

        # subtitle window initialization
        self.root = tk.Tk()

        # settings window
        self.settings: SettingsWindow

        def create_settings_window() -> None:
            self.settings = SettingsWindow(
                self.root, subtitle_generator.model_info, self.__close_settings
            )

        # continued - subtitle window initialization
        target_x = round((self.root.winfo_screenwidth() / 2) - (width / 2))
        target_y = round(self.root.winfo_screenheight() - (height * 1.5))
        self.root.wm_geometry(f"{width}x{height}+{target_x}+{target_y}")
        self.root.wm_overrideredirect(True)

        if os.name == "posix":
            self.root.wait_visibility(self.root)
        self.root.wm_attributes("-alpha", 0.75)

        self.topbar = tk.Frame(self.root, background="black", borderwidth=0)
        self.topbar.place(x=0, y=0, relwidth=1.0, height=self.root.winfo_height() / 10)

        self.__button(
            self.subtitle_generator.stop,
            resourcepath("x.png"),
            _BUTTON_RED,
            side="right",
        )
        self.__button(
            create_settings_window,
            resourcepath("settings.png"),
            _BUTTON_GREY,
            side="left",
        )

        self.text_widget = tk.Text(
            self.root,
            font=("Arial", 20),
            wrap=tk.WORD,
            background="black",
            foreground="white",
            borderwidth=0,
            highlightthickness=0,
        )
        self.text_widget.place(x=0, rely=0.1, relwidth=1.0, relheight=0.9, anchor=tk.NW)

        self.root.configure(background="#000000")

        self.text_widget.bind("<Button-1>", self.__start_drag)
        self.text_widget.bind("<B1-Motion>", self.__drag_window)

        self.root.bind("<Button-1>", self.__start_drag)
        self.root.bind("<B1-Motion>", self.__drag_window)

    def __close_settings(self) -> None:
        result = self.settings.close()
        if result != None:
            self.subtitle_generator = result
            self.subtitle_generator.start()

    def __button(
        self,
        command: tk._ButtonCommand,
        image_path: str,
        activecolor: str,
        side: Literal["left", "right"],
        image_scale: int = 13,  # i pulled 13 out my ass
    ) -> None:
        button_height = round(self.root.winfo_height() / 10)
        button_width = round(self.root.winfo_height() / 10)

        image_height = round(self.root.winfo_height() / image_scale)
        image_width = round(self.root.winfo_height() / image_scale)

        button_image = Image.open(image_path)
        button_image = button_image.resize((image_width, image_height))
        button_image = ImageTk.PhotoImage(button_image)

        button = tk.Button(
            self.topbar,
            background="black",
            width=button_width,
            height=button_height,
            image=button_image,  # type: ignore
            borderwidth=0,
            highlightthickness=0,
            activebackground=activecolor,
            command=command,
        )
        if side == "left":
            button.place(
                x=0.0 + (self.left_buttons * button_width),
                rely=0.0,
                anchor=tk.NW,
            )
            self.left_buttons += 1
        else:
            button.place(
                x=self.root.winfo_width() - (self.right_buttons * button_width),
                rely=0.0,
                anchor=tk.NE,
            )
            self.right_buttons += 1

        self.anti_garbage_collection_list.append(button_image)

    def __start_drag(self, event):
        self.x_offset = event.x
        self.y_offset = event.y

    def __drag_window(self, event):
        x = event.x_root - self.x_offset
        y = event.y_root - self.y_offset
        self.root.geometry(f"+{x}+{y}")

    def __check_overflow(self) -> None:
        if self.text_widget.yview()[1] < 1.0:
            del self.subtitle_generator.text[0]  # overflow

    def loop(self) -> None:
        self.subtitle_generator.start()

        while not self.subtitle_generator.running:
            ...

        old_text = ""
        while True:
            if not self.subtitle_generator.running:
                if self.subtitle_generator.error:
                    print(self.subtitle_generator.error)
                return

            new_text = self.subtitle_generator.display_text
            if new_text != old_text:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", new_text)
                self.__check_overflow()
                old_text = new_text

            self.root.update()

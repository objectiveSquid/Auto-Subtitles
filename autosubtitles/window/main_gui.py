from __future__ import annotations

from model.model import (
    get_downloaded_models_info,
    find_model_info_by_name,
    get_downloaded_models,
    download_model,
    get_available_models,
)
from misc.path import (
    create_models_path,
    resourcepath,
    MODELS_PATH,
)
from ._utils import combobox_ignore_input, set_font_size, seticon
from generator.subtitle_generator import SubtitleGenerator
from .misc import BUTTON_GREY, BUTTON_RED, BACKGROUND_GREY
from misc.settings import write_settings, Settings

import PIL.Image as Image, PIL.ImageTk as ImageTk
import tkinter.messagebox as tk_messagebox
from typing import Callable, Literal, Any
import tkinter.ttk as ttk
import deep_translator
import tkinter as tk
import copy
import os


class SettingsWindow:
    def __init__(
        self,
        root: tk.Misc,
        settings: Settings,
        apply_callback: Callable[[], Any],
    ) -> None:
        self.lines = 0
        get_available_models()
        create_models_path()

        self.old_settings = copy.copy(settings)
        self.settings = copy.copy(settings)
        self.parent = root
        self.window = tk.Toplevel(self.parent, background=BACKGROUND_GREY)
        self.window.wm_geometry("400x600")
        self.window.wm_resizable(False, False)

        self.window.wm_title("Auto Subtitles Settings")
        seticon(self.window, resourcepath("settings.png"))

        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            text="Select model",
        ).pack(fill=tk.X)

        self.selected_model_category = tk.StringVar(
            self.window, value=self.old_settings.model_info.category
        )
        category_select = ttk.Combobox(
            self.window,
            textvariable=self.selected_model_category,
            values=list(get_available_models().keys()),
        )
        combobox_ignore_input(category_select)
        category_select.bind(
            "<<ComboboxSelected>>",
            lambda event: self.__set_model_category(self.selected_model_category),
        )
        category_select.pack()

        self.selected_model = tk.StringVar(
            self.window,
            value=self.old_settings.model_name,
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
        combobox_ignore_input(self.model_select)
        self.model_select.bind(
            "<<ComboboxSelected>>",
            lambda event: self.__check_model_download(self.selected_model),
        )
        self.model_select.pack()

        self.download_model_warning = tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            font=("Arial", 10),
        )
        self.download_model_warning.pack()

        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            text="Subtitle font size",
        ).pack(fill=tk.X)
        self.text_size_value = tk.StringVar(
            self.window, value=str(self.settings.font_size)
        )

        def update_font_size() -> None:
            self.settings.font_size = int(self.text_size_value.get())
            self.__check_apply_button_color()

        ttk.Spinbox(
            self.window,
            textvariable=self.text_size_value,
            from_=5,
            to=100,
            increment=5,
            command=update_font_size,
        ).pack()

        self.__whitespace(10)

        def update_transparency() -> None:
            self.settings.alpha_value = float(self.transparency_value.get())
            self.__check_apply_button_color()

        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            text="Subtitle window transparency",
        ).pack(fill=tk.X)
        self.transparency_value = tk.StringVar(
            self.window, value=str(self.settings.alpha_value)
        )

        ttk.Spinbox(
            self.window,
            textvariable=self.transparency_value,
            from_=0,
            to=1,
            increment=0.1,
            command=update_transparency,
        ).pack()

        self.__whitespace(10)

        def update_translation_language() -> None:
            self.settings.translation_language = (
                self.translation_language.get().casefold()
            )
            if self.settings.translation_language == "do not translate":
                self.settings.translation_language = None
            self.__check_apply_button_color()

        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            foreground="#FFFFFF",
            text="Translation language",
        ).pack(fill=tk.X)
        self.translation_lang = tk.StringVar(
            self.window, value=str(self.settings.translation_language)
        )

        self.translation_language = tk.StringVar(
            self.window,
            value=(
                self.settings.translation_language.capitalize()
                if self.settings.translation_language != None
                else "Do not translate"
            ),
        )
        translation_language_select = ttk.Combobox(
            self.window,
            textvariable=self.translation_language,
            values=["Do not translate"] + [lang.capitalize() for lang in deep_translator.GoogleTranslator().get_supported_languages()],  # type: ignore
        )
        combobox_ignore_input(translation_language_select)
        translation_language_select.bind(
            "<<ComboboxSelected>>", lambda event: update_translation_language()
        )
        translation_language_select.pack()

        # exit button
        tk.Button(
            self.window,
            text="Close settings",
            font=("Arial", 8),
            command=self.close,
        ).pack(side=tk.RIGHT, anchor=tk.SE, padx=10, pady=10)

        # apply button
        self.apply_button = tk.Button(
            self.window,
            text="Apply settings",
            font=("Arial", 8),
            command=apply_callback,
            state=tk.DISABLED,
        )
        self.apply_button.pack(side=tk.RIGHT, anchor=tk.SE, pady=10)

        self.__check_model_download(self.selected_model)

    def __whitespace(self, size: int) -> None:
        tk.Label(
            self.window,
            background=BACKGROUND_GREY,
            font=("Arial", size),
        ).pack()

    def __check_apply_button_color(self) -> None:
        if self.old_settings == self.settings:
            self.apply_button["state"] = tk.DISABLED
        else:
            self.apply_button["state"] = tk.NORMAL

    def __check_model_download(self, modelname: tk.StringVar | str) -> None:
        if isinstance(modelname, tk.StringVar):
            modelname = modelname.get()
        self.settings.model_name = modelname
        self.__check_apply_button_color()

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
            self.selected_model.set(category_model_infos[0].name)
        else:
            self.selected_model.set(self.model_select["values"][0])

        self.__check_model_download(self.selected_model)

    def close(self) -> None:
        if self.settings != self.old_settings:
            # dont know how this works, but it does :)
            self.window.master.wm_withdraw()  # type: ignore
            self.window.master.attributes("-topmost", True)  # type: ignore
            exit_anyway = tk_messagebox.askyesno(
                "You have unsaved changes!",
                "You have unsaved changes in text size, are you sure you want to exit?",
            )
            self.window.master.wm_deiconify()  # type: ignore
            if not exit_anyway:
                return

        self.window.destroy()

    def apply(self) -> tuple[SubtitleGenerator | None, int, float, str | None]:
        new_generator = None

        self.apply_button["state"] = tk.DISABLED

        if self.selected_model.get() not in get_downloaded_models():
            download_model(self.window, self.settings.model_info.link)

        if self.old_settings.model_name != self.settings.model_name:
            new_generator = SubtitleGenerator(
                f"{MODELS_PATH}/{self.selected_model.get()}", self.settings.model_info
            )

        self.old_settings = copy.copy(self.settings)

        write_settings(self.settings)

        return (
            new_generator,
            self.settings.font_size,
            self.settings.alpha_value,
            self.settings.translation_language,
        )


class SubtitleWindow:
    def __init__(
        self,
        width: int,
        height: int,
        subtitle_generator: SubtitleGenerator,
        settings: Settings,
    ) -> None:
        self.subtitle_generator = subtitle_generator
        self.settings = settings

        self.anti_garbage_collection_list = []
        self.left_buttons = 0
        self.right_buttons = 0

        # subtitle window initialization
        self.root = tk.Tk()

        # settings window
        self.settings_window: SettingsWindow

        # continued - subtitle window initialization
        target_x = round((self.root.winfo_screenwidth() / 2) - (width / 2))
        target_y = round(self.root.winfo_screenheight() - (height * 1.5))
        self.root.wm_geometry(f"{width}x{height}+{target_x}+{target_y}")
        self.root.wm_overrideredirect(True)
        self.root.wm_resizable(False, False)

        if os.name == "posix":
            self.root.wait_visibility(self.root)
        self.root.wm_attributes("-alpha", self.settings.alpha_value)

        self.topbar = tk.Frame(self.root, background="black", borderwidth=0)
        self.topbar.place(x=0, y=0, relwidth=1.0, height=self.root.winfo_height() / 10)

        self.__button(
            self.subtitle_generator.stop,
            resourcepath("x.png"),
            BUTTON_RED,
            side="right",
        )
        self.__button(
            self.__create_settings_window,
            resourcepath("settings.png"),
            BUTTON_GREY,
            side="left",
        )

        self.text_widget = tk.Text(
            self.root,
            font=("Arial", self.settings.font_size),
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

    def __create_settings_window(self) -> None:
        self.settings_window = SettingsWindow(
            self.root, self.settings, self.__apply_settings
        )

    def __apply_settings(self) -> None:
        new_generator, new_font_size, new_alpha_value, new_translation_language = (
            self.settings_window.apply()
        )
        self.settings.translation_language = new_translation_language

        if new_generator != None:
            self.subtitle_generator.stop()

            self.subtitle_generator = new_generator
            self.subtitle_generator.start()

        set_font_size(self.text_widget, new_font_size)

        self.root.wm_attributes("-alpha", new_alpha_value)

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

    def __start_drag(self, event: tk.Event) -> None:
        self.x_offset = event.x
        self.y_offset = event.y

    def __drag_window(self, event: tk.Event) -> None:
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
                if self.settings.translation_language != None:
                    self.text_widget.insert("1.0", self.settings.translator.translate(new_text))  # type: ignore
                else:
                    self.text_widget.insert("1.0", new_text)
                self.__check_overflow()
                old_text = new_text

            self.root.update()

from model.model import get_downloaded_models_info, load_previous_model
from misc.settings import write_settings, load_settings, Settings
from generator.subtitle_generator import SubtitleGenerator
from misc.path import should_run_startwindow, MODELS_PATH
from window.main_gui import SubtitleWindow
from misc.other import SUCCESS_EXIT_CODE
from window.start import StartWindow

import tkinter.messagebox as tk_messagebox
import argparse
import shutil
import os


def main() -> int:
    parser = argparse.ArgumentParser(prog="autosubtitles")
    parser.add_argument(
        "--do_not_install_requirements",
        action="store_true",
        help="do not install automatically pip requirements",
    )  # this is only here for showing it when using --help, the functionality is used in __main__.py
    parser.add_argument(
        "--reset",
        action="store_true",
        help="reset all settings, revert to the default values and exit",
    )
    parser.add_argument(
        "--delete_models",
        help="deletes models from a comma separated list (or 'all') and exit",
    )
    args = parser.parse_args()

    if args.reset:
        write_settings(Settings())
        return SUCCESS_EXIT_CODE

    if args.delete_models:
        if args.delete_models == "all":
            shutil.rmtree(MODELS_PATH)
            os.makedirs(MODELS_PATH, exist_ok=True)
        else:
            for model_name in args.delete_models.split(","):
                model_path = f"{MODELS_PATH}/{model_name.strip()}"
                if os.path.exists(model_path):
                    shutil.rmtree(model_path)

        return SUCCESS_EXIT_CODE

    reset_settings = False
    if (settings := load_settings()) == None:
        tk_messagebox.showwarning(
            "Error in internal files",
            "Error loading settings, resetting to the default values.",
        )
        reset_settings = True
        settings = Settings()

    if should_run_startwindow():
        startwindow = StartWindow()
        while startwindow.generator == None:
            startwindow.window.update()
        generator = startwindow.generator
    else:
        generator = load_previous_model(settings)
        if generator == None:
            fallback_model = get_downloaded_models_info(sort=True)[0]
            if not reset_settings:
                tk_messagebox.showerror(
                    "Error in internal files",
                    f'Error loading previously used model, selecting "{fallback_model.name}" instead',
                )
            settings.model_name = fallback_model.name
            write_settings(settings)
            generator = SubtitleGenerator(
                f"{MODELS_PATH}/{fallback_model.name}", fallback_model
            )

    window = SubtitleWindow(600, 250, generator, settings)
    window.loop()

    write_settings(settings)

    return SUCCESS_EXIT_CODE

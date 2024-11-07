from model.model import get_downloaded_models_info, load_previous_model, scrape_models
from misc.path import write_previous_model_file, should_run_startwindow, models_path
from generator.subtitle_generator import SubtitleGenerator
from window.main_gui import SubtitleWindow
from window.start import StartWindow

import tkinter.messagebox as tk_messagebox


def main() -> None:
    if should_run_startwindow():
        startwindow = StartWindow()
        while startwindow.generator == None:
            startwindow.window.update()
        generator = startwindow.generator
    else:
        generator = load_previous_model()
        if generator == None:
            fallback_model = get_downloaded_models_info(sort=True)[0]
            tk_messagebox.showerror(
                "Error in internal files", f'Error loading previously used model, selecting "{fallback_model.name}"'  # type: ignore
            )
            write_previous_model_file(fallback_model.name)  # type: ignore
            generator = SubtitleGenerator(
                f"{models_path}/{fallback_model.name}", fallback_model  # type: ignore
            )

    window = SubtitleWindow(600, 250, generator)
    window.loop()

    write_previous_model_file(window.subtitle_generator.model_info.name)


if __name__ == "__main__":
    main()

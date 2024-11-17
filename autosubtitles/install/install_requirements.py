from .installing_window import InstallRequirementsWindow
from misc.other import without
import contextlib
import threading
import io

import pip._internal.cli.main as pip_main


REQUIREMENTS = [
    "vosk",
    "soundcard",
    "pillow",
    "requests",
    "bs4",
    "opencv-python",
    "deep-translator",
]


def process_install_output(
    output: io.StringIO, pip_return_code_output: io.StringIO, requirements: list[str]
) -> None:
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        pip_return_code_output.write(str(pip_main.main(["install"] + requirements)))


def process_freeze_output() -> list[str]:
    with contextlib.redirect_stdout(io.StringIO()) as output:
        pip_main.main(["freeze"])
        return [
            line.split("==")[0].casefold() for line in output.getvalue().splitlines()
        ]


def install_requirements(with_gui: bool = False) -> int:
    new_requirements = without(REQUIREMENTS, process_freeze_output())

    if len(new_requirements) == 0:
        return 0

    if with_gui:
        pip_output = io.StringIO()
        pip_return_code_output = io.StringIO()

        pip_thread = threading.Thread(
            target=process_install_output,
            args=(pip_output, pip_return_code_output, new_requirements),
        )
        pip_thread.start()

        window = InstallRequirementsWindow(pip_output)
        window.loop(pip_thread.is_alive)

        return int(pip_return_code_output.getvalue())
    else:
        return pip_main.main(["install"] + new_requirements)

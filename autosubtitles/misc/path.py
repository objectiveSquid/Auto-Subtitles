import os


if os.name == "nt":
    # ignore error because there is always a LOCALAPPDATA variable on windows
    MAIN_DIRECTORY = os.getenv("LOCALAPPDATA") + "/autosubtitles"  # type: ignore
else:
    # ignore error because there is always a HOME variable on posix
    MAIN_DIRECTORY = os.getenv("HOME") + "/.local/share/autosubtitles"  # type: ignore

SETTINGS_PATH = f"{MAIN_DIRECTORY}/settings.json"
MODELS_PATH = f"{MAIN_DIRECTORY}/models"


def relpath(root: str, relative: str) -> str:
    if os.path.isfile(root):
        return f"{os.path.split(root)[0]}/{relative}"
    else:
        return f"{root}/{relative}"


def resourcepath(name: str) -> str:
    return relpath(__file__, f"../resources/{name}")


def create_models_path() -> str:
    os.makedirs(MODELS_PATH, exist_ok=True)
    return MODELS_PATH


def should_run_startwindow() -> bool:
    return len(os.listdir(create_models_path())) == 0

import os


if os.name == "nt":
    # ignore error because there is always a LOCALAPPDATA variable on windows
    maindir = os.getenv("LOCALAPPDATA") + "/autosubtitles"  # type: ignore
else:
    # ignore error because there is always a HOME variable on posix
    maindir = os.getenv("HOME") + "/.local/share/autosubtitles"  # type: ignore

previous_model_path = f"{maindir}/previous_model.txt"
models_path = f"{maindir}/models"


def relpath(root: str, relative: str) -> str:
    if os.path.isfile(root):
        return f"{os.path.split(root)[0]}/{relative}"
    else:
        return f"{root}/{relative}"


def resourcepath(name: str) -> str:
    return relpath(__file__, f"../resources/{name}")


def write_previous_model_file(modelname: str) -> None:
    os.makedirs(os.path.split(previous_model_path)[0], exist_ok=True)
    with open(previous_model_path, "w") as previous_model_fp:
        previous_model_fp.write(modelname)


def create_models_path() -> str:
    os.makedirs(models_path, exist_ok=True)
    return models_path


def should_run_startwindow() -> bool:
    return len(os.listdir(create_models_path())) == 0

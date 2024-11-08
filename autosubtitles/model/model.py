from generator.subtitle_generator import SubtitleGenerator
from misc.path import previous_model_path, models_path
from window.misc import ProgressWindow
from misc.zip import unzip

import tkinter as tk
import dataclasses
import cachetools
import requests
import bs4
import os


@dataclasses.dataclass(frozen=True)
class ModelInfo:
    link: str
    name: str
    size: str
    notes: str | None  # for case restoration and punctuation models
    category: str
    license: str


def find_model_info_by_name(modelname: str) -> ModelInfo | None:
    for category in scrape_models().values():
        for modelinfo in category:
            if modelinfo.name == modelname:
                return modelinfo


def load_previous_model() -> SubtitleGenerator | None:
    try:
        with open(previous_model_path, "r") as previous_model_fp:
            previous_model_name = previous_model_fp.read()
    except OSError:
        return

    previous_model_info = find_model_info_by_name(previous_model_name)
    return SubtitleGenerator(f"{models_path}/{previous_model_name}", previous_model_info)  # type: ignore


def get_downloaded_models() -> list[str]:
    return os.listdir(models_path)


def get_downloaded_models_info(
    sort: bool = False,
    category: str | None = None,
) -> list[ModelInfo | None]:
    output = [
        find_model_info_by_name(modelname) for modelname in get_downloaded_models()
    ]

    if category:
        output = [modelinfo for modelinfo in output if modelinfo.category == category]  # type: ignore

    if sort:
        return sorted(output, key=lambda modelinfo: modelinfo.name)  # type: ignore

    return output


def download_model(master: tk.Misc, link: str) -> None:
    modelname = link.removeprefix("https://alphacephei.com/vosk/models/").removesuffix(
        ".zip"
    )
    if modelname in get_downloaded_models():
        return

    temp_zip_file = f"{models_path}/{modelname}.tmp.zip"

    response = requests.get(link, stream=True)
    downloaded_content = 0
    model_size = response.headers.get("content-length")
    if model_size != None:
        try:
            model_size = int(model_size)
        except ValueError:
            model_size = None

    progresswindow = ProgressWindow(
        master,
        None if model_size == None else round(model_size / 1024),
        modelname,
    )

    with open(temp_zip_file, "wb") as zip_file_fp:
        for chunk in response.iter_content(1024):
            zip_file_fp.write(chunk)
            downloaded_content += len(chunk)

            if model_size != None:
                progresswindow.progress_bar.step(1)
                progresswindow.progress_label.configure(
                    text=f"{round(downloaded_content / (1024 * 1024), 1):,}MB/{round(model_size / (1024 * 1024), 1):,}MB"
                )

            master.update()

    progresswindow.startunzip()
    unzip(temp_zip_file, models_path)
    progresswindow.close()

    os.remove(temp_zip_file)


@cachetools.cached({})
def scrape_models() -> dict[str, list[ModelInfo]]:
    models = {}
    latest_group = None
    recasepunc = False

    soup = bs4.BeautifulSoup(
        requests.get("https://alphacephei.com/vosk/models").text, "html.parser"
    )
    for line in soup.find_all("tr"):
        line: bs4.Tag

        if not (column := line.find("td")):
            continue
        if isinstance(group := column.find("strong"), (bs4.Tag, bs4.NavigableString)):
            if not column.find_next(attrs={"id": "punctuation-models"}):
                recasepunc = True
            else:
                recasepunc = False
            latest_group = group.text
            if recasepunc:
                latest_group += " (Punctuation)"
            models[latest_group] = []
            continue

        if latest_group == None:
            continue

        if not isinstance(link := column.find("a"), bs4.Tag):
            continue
        if (link := link.attrs.get("href")) == None:
            continue
        name = column.text

        if not isinstance(column := column.find_next_sibling("td"), bs4.Tag):
            continue
        size = column.text

        if recasepunc:
            errorrate = None
            notes = None
        else:
            if not isinstance(column := column.find_next_sibling("td"), bs4.Tag):
                continue
            errorrate = column.text

            if not isinstance(column := column.find_next_sibling("td"), bs4.Tag):
                continue
            notes = column.text

        if not isinstance(column := column.find_next_sibling("td"), bs4.Tag):
            continue
        license = column.text

        models[latest_group].append(
            ModelInfo(link, name, size, notes, latest_group, license)
        )

    return models

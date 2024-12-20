from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from misc.settings import Settings

from generator.subtitle_generator import SubtitleGenerator
from misc.other import REQUEST_ERROR_EXIT_CODE, without
from window.misc import ProgressWindow
from misc.path import MODELS_PATH
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
    for category in get_available_models().values():
        for modelinfo in category:
            if modelinfo.name == modelname:
                return modelinfo


def load_previous_model(settings: Settings) -> SubtitleGenerator | None:
    if settings.model_name == None:
        return
    previous_model_info = find_model_info_by_name(settings.model_name)
    if previous_model_info == None:
        return
    return SubtitleGenerator(
        f"{MODELS_PATH}/{settings.model_name}", previous_model_info
    )


def get_downloaded_models() -> list[str]:
    return os.listdir(MODELS_PATH)


def get_downloaded_models_info(
    sort: bool = False,
    category: str | None = None,
) -> list[ModelInfo]:
    output: list[ModelInfo] = without(
        [find_model_info_by_name(modelname) for modelname in get_downloaded_models()],
        None,
    )  # type: ignore

    if category:
        output = [modelinfo for modelinfo in output if modelinfo.category == category]

    if sort:
        output = without(
            sorted(
                output,
                key=lambda modelinfo: (modelinfo.name if modelinfo != None else 0),
            ),
            0,
        )

    return output


def download_model(master: tk.Misc, link: str) -> None:
    download_chunksize = 1024 * 1024  # 1 MB
    modelname = link.removeprefix("https://alphacephei.com/vosk/models/").removesuffix(
        ".zip"
    )
    if modelname in get_downloaded_models():
        return

    temp_zip_file = f"{MODELS_PATH}/{modelname}.tmp.zip"

    response = requests.get(link, stream=True)
    downloaded_content = 0
    model_size = response.headers.get("content-length")
    if model_size != None:
        try:
            model_size = int(model_size)
        except ValueError:
            model_size = None

    progresswindow = ProgressWindow(master, model_size, modelname)

    with open(temp_zip_file, "wb") as zip_file_fp:
        for chunk in response.iter_content(download_chunksize):
            zip_file_fp.write(chunk)
            downloaded_content += len(chunk)

            if model_size != None:
                progresswindow.progress_bar.step(len(chunk))
                progresswindow.progress_label.configure(
                    text=f"{round(downloaded_content / (1024 * 1024)):,}MB/{round(model_size / (1024 * 1024)):,}MB"
                )

            master.update()

    progresswindow.startunzip()
    unzip(temp_zip_file, MODELS_PATH)
    progresswindow.close()

    os.remove(temp_zip_file)


@cachetools.cached({})
def get_available_models(*, no_ssl_verify: bool = False) -> dict[str, list[ModelInfo]]:
    models = {}
    latest_group = None
    recasepunc = False

    try:
        soup = bs4.BeautifulSoup(
            requests.get(
                "https://alphacephei.com/vosk/models", verify=not no_ssl_verify
            ).text,
            "html.parser",
        )
    except requests.exceptions.SSLError as error:
        if tk_messagebox.askyesno(
            "Error downloading model list",
            "There was an SSL error downloading the model list, would you like to try without verifying ssl certificates?",
        ):
            return get_available_models(no_ssl_verify=True)
        exit(REQUEST_ERROR_EXIT_CODE)
    except requests.RequestException as error:
        if tk_messagebox.askyesno(
            "Error downloading model list",
            f"There was an error downloading the model list: {error}\nWould you like to try again?",
        ):
            return get_available_models()
        exit(REQUEST_ERROR_EXIT_CODE)

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

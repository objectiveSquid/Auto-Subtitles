from __future__ import annotations

from .path import SETTINGS_PATH

from model.model import get_downloaded_models_info, find_model_info_by_name, ModelInfo
import dataclasses
import json


DEFAULT_FONT_SIZE = 20
DEFAULT_ALPHA_VALUE = 0.75


@dataclasses.dataclass
class Settings:
    model_name: str = None  # type: ignore
    font_size: int = DEFAULT_FONT_SIZE
    alpha_value: float = DEFAULT_ALPHA_VALUE

    def __post_init__(self) -> None:
        self.__prev_model_name = None

        if self.model_name == None:
            self.model_name = get_downloaded_models_info(sort=True)[0].name

    @property
    def model_info(self) -> ModelInfo:
        if self.__prev_model_name == self.model_name:
            return self.__model_info

        self.__prev_model_name = self.model_name
        self.__model_info: ModelInfo = find_model_info_by_name(self.model_name)  # type: ignore

        return self.__model_info

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Settings):
            return False
        return (
            self.model_name == other.model_name
            and self.font_size == other.font_size
            and self.alpha_value == other.alpha_value
        )

    @property
    def as_json(self) -> dict[str, str | int | float | None]:
        return {
            "model_name": self.model_name,
            "font_size": self.font_size,
            "alpha_value": self.alpha_value,
        }

    @classmethod
    def from_json(cls, json_data: dict[str, str]) -> Settings:
        return cls(
            model_name=json_data["model_name"],
            font_size=int(json_data["font_size"]),
            alpha_value=float(json_data["alpha_value"]),
        )


def load_settings() -> Settings | None:
    try:
        with open(SETTINGS_PATH, "r") as settings_fp:
            return Settings.from_json(json.load(settings_fp))
    except (json.JSONDecodeError, OSError, ValueError):
        return


def write_settings(new_settings: Settings) -> bool:
    if new_settings == None:
        new_settings = settings
    try:
        with open(SETTINGS_PATH, "w") as settings_fp:
            json.dump(new_settings.as_json, settings_fp)
    except OSError:
        return False

    return True

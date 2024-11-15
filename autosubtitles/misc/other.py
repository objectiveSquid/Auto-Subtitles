from typing import Any


def without[T](input_list: list[T], element: Any | list[Any]) -> list[T]:
    if isinstance(element, list):
        return [item for item in input_list if item not in element]
    return [item for item in input_list if item != element]


SUCCESS_EXIT_CODE = 0
FAILURE_EXIT_CODE = 1
REQUEST_ERROR_EXIT_CODE = 2
PIP_MISSING_EXIT_CODE = 3
PIP_ERROR_EXIT_CODE = 4

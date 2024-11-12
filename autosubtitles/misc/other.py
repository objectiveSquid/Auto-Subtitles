from typing import Any


def without[T](list: list[T], element: Any) -> list[T]:
    return [item for item in list if item != element]


SUCCESS_EXIT_CODE = 0
FAILURE_EXIT_CODE = 1
REQUEST_ERROR_EXIT_CODE = 2

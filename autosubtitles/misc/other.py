from typing import Any


def without[T](list: list[T], element: Any) -> list[T]:
    return [item for item in list if item != element]

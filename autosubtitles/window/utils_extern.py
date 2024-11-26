import tkinter as tk


def normalize_window_size(
    root: tk.Misc,
    geometry: tuple[int, int, int | None, int | None],
    from_size: tuple[int, int] = (1920, 1080),
) -> str:
    x_relation = root.winfo_screenwidth() / from_size[0]
    y_relation = root.winfo_screenheight() / from_size[1]

    width = round(geometry[0] * x_relation)
    height = round(geometry[1] * y_relation)
    x = round(geometry[2] * x_relation) if geometry[2] != None else None
    y = round(geometry[3] * y_relation) if geometry[3] != None else None

    return f"{width}x{height}{f'+{x}' if x else ''}{f'+{y}' if y else ''}"

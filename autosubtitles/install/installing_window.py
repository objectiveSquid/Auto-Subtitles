from window.utils_extern import normalize_window_size

from typing import Callable
import tkinter as tk
import io


class InstallRequirementsWindow:
    def __init__(self, pip_output: io.StringIO) -> None:
        self.pip_output = pip_output

        self.window = tk.Tk()
        self.window.configure(background="#333333")
        self.window.wm_geometry(
            normalize_window_size(self.window, (500, 300, None, None))
        )
        self.window.wm_title("Installing requirements")
        self.window.wm_resizable(False, False)

        tk.Label(
            self.window,
            text="Pip output:",
            background="#333333",
            foreground="#FFFFFF",
        ).pack()

        self.pip_output_box = tk.Text(
            self.window,
            background="#555555",
            foreground="#FFFFFF",
            borderwidth=3,
            state=tk.DISABLED,
        )
        self.pip_output_box.pack()

    def loop(self, while_function: Callable[[], bool]) -> None:
        while while_function():
            self.pip_output_box.configure(state=tk.NORMAL)

            self.pip_output_box.insert("1.0", tk.END)
            self.pip_output_box.insert(tk.END, self.pip_output.getvalue())
            self.pip_output_box.see(tk.END)

            self.pip_output_box.configure(state=tk.DISABLED)

            self.window.update()

        self.window.destroy()

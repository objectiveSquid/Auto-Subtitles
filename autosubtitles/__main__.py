from misc.other import PIP_MISSING_EXIT_CODE, PIP_ERROR_EXIT_CODE

import tkinter.messagebox as tk_messagebox
import sys


if "--do_not_install_requirements" in sys.argv:
    from after_install import main

    exit(main())

try:
    import pip
except ImportError:
    tk_messagebox.showerror(
        "Missing package", "Pip is not installed, please install it."
    )
    exit(PIP_MISSING_EXIT_CODE)

from install.install_requirements import install_requirements

if install_requirements(True) != 0:
    tk_messagebox.showerror(
        "Error installing requirements",
        "There was an error automatically installing the requirements, please do so manually, there is a guide in the readme file.",
    )
    exit(PIP_ERROR_EXIT_CODE)

from after_install import main

exit(main())

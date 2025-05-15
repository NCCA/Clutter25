#!/usr/bin/env -S uv run --script

import sys

from qtpy.QtWidgets import QApplication

from ClutterDialog import ApplicationMode, ClutterDialog

mode = ApplicationMode.STANDALONE
# using import discovery so need to enable ruff noqa : F401 so unused imports are not removed
try:
    import maya.cmds as cmds  # noqa: F401

    mode = ApplicationMode.MAYA
except ModuleNotFoundError:
    pass

try:
    import hou  # noqa: F401

    mode = ApplicationMode.HOUDINI
except ModuleNotFoundError:
    pass


def run_dcc():
    print(f"Running in DCC mode {mode}")
    dialog = ClutterDialog(mode)
    dialog.show()


def run_houdini():
    print("running in houdini mode")
    import hou

    dialog = ClutterDialog(mode, parent=hou.qt.mainWindow())
    # dialog.show()
    dialog.exec()


def run_standalone():
    print("running Standalone")
    app = QApplication(sys.argv)
    dialog = ClutterDialog(mode)
    dialog.load_database("../ClutterTest.db")
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    if mode == ApplicationMode.STANDALONE:
        run_standalone()
    else:
        run_dcc()

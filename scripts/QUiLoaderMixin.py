from PySide6.QtCore import QFile, QIODevice, QObject
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget


class QUiLoaderMixin:
    def load_ui(self, path: str, baseinstance: QWidget = None):
        """Load a .ui file from disk or Qt resource path and attach widgets to self."""
        loader = QUiLoader()
        file = QFile(path)

        if not file.exists():
            raise FileNotFoundError(f"UI file not found: {path}")

        if not file.open(QIODevice.ReadOnly):
            raise IOError(f"Failed to open UI file: {path}")

        # Load the .ui form
        ui = loader.load(file, baseinstance or self)
        file.close()

        if ui is None:
            raise RuntimeError(f"Failed to load UI from {path}")

        # Bind named children directly to self as attributes
        for obj in ui.findChildren(QObject):
            name = obj.objectName()
            if name and not hasattr(self, name):
                setattr(baseinstance, name, obj)

        return ui

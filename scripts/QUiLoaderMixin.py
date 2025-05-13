from qtpy.QtCore import QFile, QIODevice, QObject
from qtpy.QtUiTools import QUiLoader
from qtpy.QtWidgets import QWidget


class QUiLoaderMixin:
    """
    Mixin class to simplify loading Qt Designer .ui files and binding their widgets as attributes.

    This mixin provides a `load_ui` method that loads a .ui file (from disk or Qt resource path)
    and attaches all named child widgets as attributes to self.

    Usage:
        class MyWidget(QWidget, QUiLoaderMixin):
            def __init__(self):
                super().__init__()
                self.load_ui("path/to/file.ui", parent=self)
                # Now you can access widgets by their objectName, e.g., self.pushButton
                # can also use resource version :/path/in/rc/file
    """

    def load_ui(self, path: str, parent: QWidget) -> QWidget:
        """
        Load a .ui file and attach its named child widgets as attributes.

        Args:
            path (str): Path to the .ui file (filesystem or Qt resource path).
            parent (QWidget): The parent widget for the loaded UI. typically is will be self

        Returns:
            QWidget: The top-level widget loaded from the .ui file.

        Raises:
            FileNotFoundError: If the .ui file does not exist.
            IOError: If the .ui file cannot be opened.
            RuntimeError: If the .ui file cannot be loaded.
        """
        loader = QUiLoader()
        file = QFile(path)

        if not file.exists():
            raise FileNotFoundError(f"UI file not found: {path}")

        if not file.open(QIODevice.ReadOnly):
            raise IOError(f"Failed to open UI file: {path}")

        ui = loader.load(file, parent)
        file.close()

        if ui is None:
            raise RuntimeError(f"Failed to load UI from {path}")

        # Bind named children directly to self as attributes
        for obj in ui.findChildren(QObject):
            name = obj.objectName()
            if name and not hasattr(self, name):
                setattr(parent, name, obj)

        return ui

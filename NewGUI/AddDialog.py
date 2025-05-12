import sys
from pathlib import Path
from typing import Optional

from qtpy.QtCore import QByteArray, Slot
from qtpy.QtGui import QPixmap
from qtpy.QtSql import QSqlDatabase, QSqlQuery
from qtpy.QtWidgets import QApplication, QDialog, QFileDialog, QWidget
from qtpy.uic import loadUi

from sql_queries import QUERIES


class AddDialog(QDialog):
    """
    Dialog for adding a new item to the database, including images and mesh files as BLOBs.

    Attributes:
        db (QSqlDatabase): The database connection.
        front_image_blob (Optional[bytes]): Binary data for the front image.
        side_image_blob (Optional[bytes]): Binary data for the side image.
        top_image_blob (Optional[bytes]): Binary data for the top image.
        persp_image_blob (Optional[bytes]): Binary data for the perspective image.
        mesh_blob (Optional[bytes]): Binary data for the mesh file.
        _last_dir (str): Last directory used in QFileDialog for this dialog instance.
    """

    def __init__(self, db: QSqlDatabase, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the AddDialog.

        Args:
            db (QSqlDatabase): The database connection.
            parent (Optional[QWidget]): The parent widget, if any.
        """
        super().__init__(parent)
        loadUi("AddDialog.ui", self)
        self.db: QSqlDatabase = db
        self.front_image_blob: Optional[bytes] = None
        self.side_image_blob: Optional[bytes] = None
        self.top_image_blob: Optional[bytes] = None
        self.persp_image_blob: Optional[bytes] = None
        self.mesh_blob: Optional[bytes] = None
        self._last_dir: str = "./"

        self.front_image.clicked.connect(self.add_image)
        self.side_image.clicked.connect(self.add_image)
        self.persp_image.clicked.connect(self.add_image)
        self.top_image.clicked.connect(self.add_image)
        self.cancel.clicked.connect(self.reject)
        self.item_name.textChanged.connect(self.update_button_state)
        self.insert.clicked.connect(self.insert_into_db)
        self.select_mesh.clicked.connect(self.add_mesh)

    @Slot()
    def add_mesh(self) -> None:
        """
        Open a file dialog to select a mesh file and store its binary data.
        Remembers the last directory used within this dialog instance.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Mesh", self._last_dir, "Mesh files (*.obj *.fbx *.usd*)"
        )
        if file_name:
            path = Path(file_name)
            self.mesh_blob = path.read_bytes()
            self.mesh_name.setText(file_name)
            self._last_dir = str(path.parent)
            self.update_button_state()

    @Slot()
    def insert_into_db(self) -> None:
        """
        Insert the current item, including images and mesh, into the database.
        Raises:
            RuntimeError: If the query execution fails.
        Note Blob data must be a QByteArray else the query will fail.
        """
        if self.db:
            query = QSqlQuery()
            query.prepare(QUERIES["insert"])
            query.addBindValue(self.item_name.text())
            query.addBindValue(QByteArray(self.mesh_blob) if self.mesh_blob else None)
            query.addBindValue(self.mesh_type.currentText())
            query.addBindValue(QByteArray(self.top_image_blob) if self.top_image_blob else None)
            query.addBindValue(QByteArray(self.side_image_blob) if self.side_image_blob else None)
            query.addBindValue(QByteArray(self.front_image_blob) if self.front_image_blob else None)
            query.addBindValue(QByteArray(self.persp_image_blob) if self.persp_image_blob else None)

            if not query.exec():
                raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")

        self.accept()

    @Slot()
    def add_image(self) -> None:
        """
        Open a file dialog to select an image and store its binary data.
        Sets the image as the icon for the corresponding button.
        Remembers the last directory used within this dialog instance.
        """
        images = {
            "front_image": "front_image_blob",
            "side_image": "side_image_blob",
            "top_image": "top_image_blob",
            "persp_image": "persp_image_blob",
        }

        sender = self.sender()
        if sender is None:
            return

        sender_name = sender.objectName()
        target_blob_name = images.get(sender_name)

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", self._last_dir, "Image files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name and target_blob_name:
            path = Path(file_name)
            image_data = path.read_bytes()
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data):
                sender.setFixedSize(pixmap.size())
                sender.setIcon(pixmap)
                sender.setIconSize(pixmap.size())
                setattr(self, target_blob_name, image_data)
                self._last_dir = str(path.parent)

            self.update_button_state()

    def update_button_state(self) -> None:
        """
        Enable the insert button only if all required fields are filled.
        """
        name_filled: bool = bool(self.item_name.text().strip())
        self.insert.setEnabled(name_filled)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = AddDialog(None, None)
    dialog.show()
    sys.exit(app.exec_())

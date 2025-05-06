#!/usr/bin/env -S uv run --script

import sys

from qtpy.QtCore import QByteArray, Qt
from qtpy.QtGui import QPixmap

# from ui_ClutterUI import Ui_ClutterUI
from qtpy.QtSql import QSqlDatabase, QSqlQueryModel
from qtpy.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, QTableView
from qtpy.uic import loadUi


class ImageDataModel(QSqlQueryModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_columns_checked = False
        self._image_columns = set()

    def _detect_image_columns(self):
        # Only try if we have at least one row
        if self.rowCount() == 0:
            return

        for col in range(self.columnCount()):
            index = self.index(0, col)
            value = super().data(index, Qt.DisplayRole)

            if isinstance(value, QByteArray):
                test_bytes = bytes(value)
                pixmap = QPixmap()
                if pixmap.loadFromData(test_bytes):
                    self._image_columns.add(col)

        self._image_columns_checked = True

    def data(self, index, role=Qt.DisplayRole):
        if not self._image_columns_checked:
            self._detect_image_columns()

        col = index.column()

        if col in self._image_columns:
            if role in [Qt.DisplayRole, Qt.EditRole]:
                return None
            if role == Qt.DecorationRole:
                value = super().data(index, Qt.DisplayRole)
                if isinstance(value, QByteArray):
                    pixmap = QPixmap()
                    if pixmap.loadFromData(bytes(value)):
                        return pixmap
        return super().data(index, role)


class ClutterDialog(QDialog):
    def __init__(self, parent=None):
        super(ClutterDialog, self).__init__()
        loadUi("ClutterUI.ui", self)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.database_view = QTableView(self.db_view)
        self.db_layout.addWidget(self.database_view)

        self.select_db.clicked.connect(self.load_db_pressed)
        self.display_front.checkStateChanged.connect(self.update_db_view)
        self.display_side.checkStateChanged.connect(self.update_db_view)
        self.display_persp.checkStateChanged.connect(self.update_db_view)
        self.display_top.checkStateChanged.connect(self.update_db_view)
        self.run_query_button.clicked.connect(self.run_custom_query)
        self.query_text.returnPressed.connect(lambda:  self.run_query(self.query_text.text()))

    def update_db_view(self):
        if not self.db.isOpen() :
            QMessageBox.critical(
                self, "Critical Error", " Database Not Open", QMessageBox.StandardButton.Abort
            )

        # Base query
        columns = ["name", "mesh_type"]

        # Dynamically add columns based on checkboxes
        checkbox_column_map = [
            (self.display_front, "front_image"),
            (self.display_side, "side_image"),
            (self.display_persp, "persp_image"),
            (self.display_top, "top_image"),
        ]

        for checkbox, column in checkbox_column_map:
            if checkbox.isChecked():
                columns.append(column)

        # Build the final query string
        query_str = f"SELECT {', '.join(columns)} FROM Meshes;"

        # Execute the query
        self.run_query(query_str)

    def load_db_pressed(self):
        file_name = QFileDialog.getOpenFileName(
            self, "Select DB", "./", "Clutter Base Files (*.db)"
        )
        if file_name[0] != "":
            self.load_database(file_name[0])
        self.select_db.clearFocus()

    def load_database(self, file_name: str) -> None:
        self.db.setDatabaseName(file_name)
        self.connected = self.db.open()
        if "Meshes" not in self.db.tables():
            QMessageBox.critical(
                self, "Critical Error", " Not a valid DB file", QMessageBox.StandardButton.Abort
            )
        query_cols = "name,mesh_type,front_image,side_image,top_image,persp_image"
        query_str = f"select {query_cols} from Meshes;"
        self.run_query(query_str)

    def run_custom_query(self) :
        if len(self.query_text.text()) > 0 :
            self.run_query(self.query_text.text())

    def run_query(self, query_str):
        query = ImageDataModel()
        query.setQuery(query_str)
        self.database_view.setModel(query)
        self.database_view.resizeRowsToContents()
        self.database_view.resizeColumnsToContents()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ClutterDialog()
    dialog.show()
    sys.exit(app.exec_())

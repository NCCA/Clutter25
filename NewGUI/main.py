#!/usr/bin/env -S uv run --script

import sys
from typing import List, Optional, Tuple

from ImageDataModel import ImageDataModel

# from ModelViewer import ModelViewer
from PySide6.QtGui import QCloseEvent
from qtpy.QtGui import QPixmap
from qtpy.QtSql import QSqlDatabase
from qtpy.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, QTableView, QWidget
from qtpy.uic import loadUi


class ClutterDialog(QDialog):
    """
    The main dialog for the Clutter application, providing a GUI for interacting with a database of meshes.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the ClutterDialog.

        :param parent: The parent widget, if any.
        """
        super(ClutterDialog, self).__init__()
        loadUi("ClutterUI.ui", self)
        self.db: QSqlDatabase = QSqlDatabase.addDatabase("QSQLITE")
        self.database_view: QTableView = QTableView(self.db_view)
        self.db_layout.addWidget(self.database_view)
        self.view_widget: QWidget = QWidget()

        self.view_tab_layout.addWidget(self.view_widget)
        self.select_db.clicked.connect(self.load_db_pressed)
        self.display_front.checkStateChanged.connect(self.update_db_view)
        self.display_side.checkStateChanged.connect(self.update_db_view)
        self.display_persp.checkStateChanged.connect(self.update_db_view)
        self.display_top.checkStateChanged.connect(self.update_db_view)
        self.run_query_button.clicked.connect(lambda: self.run_query(self.query_text.text()))
        self.query_text.setFocus()
        self.query_text.returnPressed.connect(lambda: self.run_query(self.query_text.text()))
        self.db_view.currentChanged.connect(self.tab_view_changed)
        # setup 2nd view widget
        loadUi("ViewWidget.ui", self.view_widget)
        self.view_widget.previous_record.clicked.connect(self.update_record)
        self.view_widget.next_record.clicked.connect(self.update_record)
        # self.model_viewer = ModelViewer()
        # self.db_view.addTab(self.model_viewer, "3D View")
        self.current_view_index: int = 0

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event by closing the database connection.

        :param event: The close event.
        """
        self.db.close()

    def tab_view_changed(self, index: int) -> None:
        """
        Handle changes to the tab view.

        :param index: The index of the newly selected tab.
        """
        if index == 1 and self.db.isOpen():
            self.set_record()

    def update_record(self):
        if self.sender().objectName() == "previous_record":
            self.current_view_index -= 1
        elif self.sender().objectName() == "next_record":
            self.current_view_index += 1

        self.current_view_index = max(0, min(self.current_view_index, self.query.rowCount()))
        self.set_record()

    def set_record(self):
        num_items = self.query.rowCount()
        self.view_widget.num_records.setText(f"Num Records : {num_items} Current Record {self.current_view_index}")
        name = self.query.get_data_at_index(self.current_view_index, "name")
        mesh_type = self.query.get_data_at_index(self.current_view_index, "mesh_type")
        self.view_widget.name_label.setText(f"Item Name {name}")
        self.view_widget.type_label.setText(f"Type {mesh_type}")

        images: List[Tuple[QLabel, str]] = [
            (self.view_widget.front_image, "front_image"),
            (self.view_widget.side_image, "side_image"),
            (self.view_widget.top_image, "top_image"),
            (self.view_widget.persp_image, "persp_image"),
        ]
        pixmap = QPixmap()
        for widget, name in images:
            img = self.query.get_data_at_index(self.current_view_index, name)
            if pixmap.loadFromData(bytes(img)):
                widget.setPixmap(pixmap)

    def update_db_view(self) -> None:
        """
        Update the database view based on the selected checkboxes.
        """
        if not self.db.isOpen():
            QMessageBox.critical(self, "Critical Error", "Database not open", QMessageBox.StandardButton.Abort)
        else:
            columns: List[str] = ["name", "mesh_type"]
            checkbox_column_map: List[Tuple[QCheckBox, str]] = [
                (self.display_front, "front_image"),
                (self.display_side, "side_image"),
                (self.display_persp, "persp_image"),
                (self.display_top, "top_image"),
            ]

            for checkbox, column in checkbox_column_map:
                if checkbox.isChecked():
                    columns.append(column)

            query_str = f"SELECT {', '.join(columns)} FROM Meshes;"
            self.run_query(query_str)

    def load_db_pressed(self) -> None:
        """
        Handle the event when the "Select DB" button is pressed.
        """
        file_name = QFileDialog.getOpenFileName(self, "Select DB", "./", "Clutter Base Files (*.db)")
        if file_name[0] != "":
            self.load_database(file_name[0])
        self.query_text.setFocus()

    def load_database(self, file_name: str) -> None:
        """
        Load a database file.

        :param file_name: The path to the database file.
        """
        self.db.setDatabaseName(file_name)
        self.connected: bool = self.db.open()
        if "Meshes" not in self.db.tables():
            QMessageBox.critical(self, "Critical Error", " Not a valid DB file", QMessageBox.StandardButton.Abort)

        query_cols = "name,mesh_type,front_image,side_image,top_image,persp_image"
        query_str = f"select {query_cols} from Meshes;"
        self.run_query(query_str)
        self.current_view_index = 0

    def run_query(self, query_str: str) -> None:
        """
        Execute a SQL query and update the database view.

        :param query_str: The SQL query string to execute.
        """
        if len(query_str) > 0:
            self.query = ImageDataModel()
            self.query.setQuery(query_str)
            self.database_view.setModel(self.query)
            self.database_view.resizeRowsToContents()
            self.database_view.resizeColumnsToContents()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ClutterDialog()
    dialog.load_database("../ClutterTest.db")

    dialog.show()
    sys.exit(app.exec_())

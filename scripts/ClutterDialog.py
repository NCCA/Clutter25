import tempfile
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

from qtpy.QtCore import QResource, QSize

# from ModelViewer import ModelViewer
from qtpy.QtGui import QCloseEvent, QIcon, QPixmap
from qtpy.QtSql import QSqlDatabase, QSqlQuery
from qtpy.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QTableView,
    QWidget,
)

import rc_resources  # noqa: F401 needed for rcc
from AddDialog import AddDialog
from ImageDataModel import ImageDataModel
from QUiLoaderMixin import QUiLoaderMixin
from sql_queries import QUERIES


class ApplicationMode(Enum):
    STANDALONE = 1
    MAYA = 2
    HOUDINI = 3


class MeshImporter:
    def import_mesh(self, query):
        raise NotImplementedError()

    ...


class Maya(MeshImporter):
    def import_mesh(self, query):
        import maya.cmds as cmds

        maya_import_name = {"obj": "OBJ", "usd": "USD Import", "fbx": "FBX"}
        print(query)
        mesh_data = query.value(0)
        mesh_type = query.value(1)
        print(mesh_type, maya_import_name[mesh_type])
        with tempfile.TemporaryDirectory() as temp_dir:
            out_name = f"{temp_dir}/mesh.{mesh_type}"
            print(out_name)
            file = Path(out_name)
            file.write_bytes(mesh_data)
            cmds.file(
                out_name,
                gr=True,
                i=True,
                groupName="ClutterImport",
                type=maya_import_name[mesh_type],
            )


class Houdini(MeshImporter):
    def import_mesh(self, query): ...


class Standalone(MeshImporter):
    def import_mesh(self, query):
        mesh_type = query.value(1)

        file_name, _ = QFileDialog.getSaveFileName(
            None, "Choose Filename", "./", f"Mesh Files (*.{mesh_type})"
        )

        if file_name != "":
            mesh_data = query.value(0)
            file = Path(file_name)
            file.write_bytes(mesh_data)


class ClutterDialog(QDialog, QUiLoaderMixin):
    """
    The main dialog for the Clutter application, providing a GUI for interacting with a database of meshes.
    """

    def __init__(self, mode: ApplicationMode, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the ClutterDialog.

        :param parent: The parent widget, if any.
        """

        super(ClutterDialog, self).__init__(parent)
        QResource.registerResource("resources.rcc")
        ui = self.load_ui(":/ui/ClutterUI.ui", self)
        self.setLayout(ui.layout())
        self.db: QSqlDatabase = QSqlDatabase.addDatabase("QSQLITE")
        self.database_view: QTableView = QTableView(self.db_view)
        self.db_layout.addWidget(self.database_view)
        # create an empty widget for our view tab
        self.database_view.doubleClicked.connect(self.load_mesh)
        self.select_db.clicked.connect(self.load_db_pressed)
        self.display_front.stateChanged.connect(self.update_db_view)
        self.display_side.stateChanged.connect(self.update_db_view)
        self.display_persp.stateChanged.connect(self.update_db_view)
        self.display_top.stateChanged.connect(self.update_db_view)
        self.run_query_button.clicked.connect(
            lambda: self.run_query(self.query_text.text())
        )
        self.query_text.setFocus()
        self.query_text.returnPressed.connect(
            lambda: self.run_query(self.query_text.text())
        )
        self.db_view.currentChanged.connect(self.tab_view_changed)
        self.new_db.clicked.connect(self.new_db_clicked)
        self.delete_from_db.clicked.connect(self.delete_selected_row)
        self.insert_to_db.clicked.connect(self.add_item)
        self.query = ImageDataModel()
        self._loader = {
            ApplicationMode.STANDALONE: Standalone(),
            ApplicationMode.MAYA: Maya(),
            ApplicationMode.HOUDINI: Houdini(),
        }[mode]

        # setup 2nd view widget
        self.view_widget: QWidget = QWidget()
        ui = self.load_ui(":/ui/ViewWidget.ui", self.view_widget)
        self.view_tab_layout.addWidget(ui)
        # self.view_tab_layout.addLayout(ui.layout())
        self.view_widget.previous_record.clicked.connect(self.update_record)
        self.view_widget.previous_record.setIcon(QIcon(":/icons/arrow_left.png"))
        self.view_widget.previous_record.setIconSize(QSize(32, 32))
        self.view_widget.next_record.clicked.connect(self.update_record)
        self.view_widget.next_record.setIcon(QIcon(":/icons/arrow_right.png"))
        self.view_widget.next_record.setIconSize(QSize(32, 32))
        self.view_widget.import_mesh.clicked.connect(
            lambda: self.load_mesh(self.current_view_index)
        )
        self.current_view_index: int = 0
        self.view_widget.goto_record.valueChanged.connect(self.goto_changed)
        self.resize(1000, 700)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event by closing the database connection.

        :param event: The close event.
        """
        self.db.close()

    def new_db_clicked(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Choose new db name", "./", "Clutter Base Files (*.db)"
        )
        if file_name != "":
            self.db.setDatabaseName(file_name[0])
            self.db.open()
            if not self.db.open():
                raise RuntimeError(
                    f"Failed to create or open database: {self.db.lastError().text()}"
                )
            # need to run base query here to create a new table.
            query = QSqlQuery()
            if not query.exec(QUERIES["drop_table"]):
                raise RuntimeError(
                    f"Failed to execute query: {query.lastError().text()}"
                )

            if not query.exec(QUERIES["new_db"]):
                raise RuntimeError(
                    f"Failed to execute query: {query.lastError().text()}"
                )
            self.query = ImageDataModel()

    def tab_view_changed(self, index: int) -> None:
        """
        Handle changes to the tab view.

        :param index: The index of the newly selected tab.
        """
        if index == 1 and self.db.isOpen():
            self.set_record()

    def goto_changed(self, index):
        self.current_view_index = index
        self.set_record()

    def update_record(self):
        if self.sender().objectName() == "previous_record":
            self.current_view_index -= 1
        elif self.sender().objectName() == "next_record":
            self.current_view_index += 1

        self.current_view_index = max(
            0, min(self.current_view_index, self.query.rowCount())
        )
        self.view_widget.goto_record.setValue(self.current_view_index)
        self.set_record()

    def set_record(self):
        num_items = self.query.rowCount()
        self.view_widget.goto_record.setMaximum(num_items)
        self.view_widget.num_records.setText(
            f"Num Records : {num_items} Current Record {self.current_view_index}"
        )
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
                pixmap.scaled(widget.size())
                widget.setPixmap(pixmap)

    def update_db_view(self) -> None:
        """
        Update the database view based on the selected checkboxes.
        """
        if not self.db.isOpen():
            QMessageBox.critical(
                self,
                "Critical Error",
                "Database not open",
                QMessageBox.StandardButton.Abort,
            )
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
        file_name = QFileDialog.getOpenFileName(
            self, "Select DB", "./", "Clutter Base Files (*.db)"
        )
        if file_name[0] != "":
            self.load_database(file_name[0])
        self.query_text.setFocus()

    def open_and_validate(self, file_name: str, validate: bool = True) -> None:
        if self.db.isOpen():
            self.db.close()
        self.db.setDatabaseName(file_name)
        self.db.open()

        if validate and "Meshes" not in self.db.tables():
            QMessageBox.critical(
                self,
                "Critical Error",
                " Not a valid DB file",
                QMessageBox.StandardButton.Abort,
            )

    def load_database(self, file_name: str) -> None:
        """
        Load a database file.

        :param file_name: The path to the database file.
        """
        self.open_and_validate(file_name)
        self.run_query(QUERIES["select_all"])
        self.current_view_index = 0

    def run_query(self, query_str: str) -> None:
        """
        Execute a SQL query and update the database view.

        :param query_str: The SQL query string to execute.
        """
        if len(query_str) > 0:
            try:
                self.query = ImageDataModel()
                self.query.setQuery(query_str)
                self.database_view.setModel(self.query)
                self.database_view.resizeRowsToContents()
                self.database_view.resizeColumnsToContents()
            except RuntimeError as e:
                print(f"error running query {query_str}: {e}")

    def add_item(self):
        dialog = AddDialog(self.db)
        dialog.show()
        if dialog.exec():
            self.run_query(QUERIES["select_all"])

    def delete_selected_row(self) -> None:
        """
        Delete the selected row(s) from the database and refresh the table view.
        Need to dynamically build the query as we don't know how may values
        """
        selected_indexes = self.database_view.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.critical(
                self,
                "No Rows Selected",
                "Select Multiple Rows to Delete",
                QMessageBox.StandardButton.Abort,
            )
            return

        # Ask for confirmation using QMessageBox
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete the selected rows?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        item_ids = []
        for index in selected_indexes:
            row = index.row()
            model = self.query
            id_column = 0  # Replace with the actual column number for 'id'
            id_index = model.index(row, id_column)
            item_ids.append(model.data(id_index))

        # Construct the placeholder string, e.g. "?, ?, ?" for three IDs.
        placeholders = ", ".join("?" for _ in item_ids)
        query_str = f"DELETE FROM Meshes WHERE id IN ({placeholders})"
        query = QSqlQuery()
        query.prepare(query_str)

        # Bind each id individually
        for item_id in item_ids:
            query.addBindValue(item_id)

        if not query.exec():
            print("Delete failed:", query.lastError().text())
        else:
            # Refresh the view or run the select query
            self.run_query(QUERIES["select_all"])

    def load_mesh(self, index):
        model = self.query
        if not isinstance(index, int):
            index = index.row()

        mesh_id = model.data(model.index(index, 0))

        query = QSqlQuery()
        query.prepare(QUERIES["extract_mesh_data"])
        query.addBindValue(mesh_id)
        result = query.exec_()
        if result:
            query.next()
            print(type(self._loader))
            self._loader.import_mesh(query)

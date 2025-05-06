#!/usr/bin/env -S uv run --script 

import sys
from qtpy.QtWidgets import QApplication,QDialog,QFileDialog,QTableView,QMessageBox
from qtpy.QtSql import QSqlDatabase,QSqlQueryModel 
from ui_ClutterUI import Ui_ClutterUI
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt

class ImageDataModel(QSqlQueryModel) :
    def __init__(self,parent=None) :
        super(ImageDataModel,self).__init__()

    def data(self,index, role=0) :
        if index.column() in [2,3,4,5] :
            if role == Qt.ItemDataRole or role == Qt.ItemDataRole.EditRole :
                return None 
            if role == Qt.ItemDataRole.DecorationRole :
                variant = QSqlQueryModel.data(self,index,Qt.ItemDataRole.DisplayRole)
                pixmap = QPixmap()
                pixmap.loadFromData(variant)
                return pixmap
        else :
            value =QSqlQueryModel.data(self,index,role)
            return value


class ClutterDialog(QDialog,Ui_ClutterUI) :
    def __init__(self,parent=None) :
        super(ClutterDialog,self).__init__()
        self.setupUi(self)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.database_view = QTableView(self.db_view)
        self.db_layout.addWidget(self.database_view)

        self.select_db.clicked.connect(self.load_db_pressed)

    def load_db_pressed(self) :
        file_name= QFileDialog.getOpenFileName(self,"Select DB","./","Clutter Base Files (*.db)")
        if file_name[0] != "" :
            self.load_database(file_name[0])

    def load_database(self, file_name : str) -> None :
        self.db.setDatabaseName(file_name)
        self.connected = self.db.open()
        if "Meshes" not in self.db.tables() :
            QMessageBox.critical(self,"Critical Error"," Not a valid DB file",
                                 QMessageBox.StandardButton.Abort)
        query = ImageDataModel()
        query_cols="name,mesh_type,front_image,side_image,top_image,persp_image"
        query.setQuery(f"select {query_cols} from Meshes;")
        self.database_view.setModel(query)
        self.database_view.resizeRowsToContents()
        self.database_view.resizeColumnsToContents()



if __name__ == "__main__" : 
    app=QApplication(sys.argv)
    dialog = ClutterDialog()
    dialog.show()
    sys.exit(app.exec_())


from typing import Any, Optional

from qtpy.QtCore import QByteArray, QModelIndex, Qt
from qtpy.QtGui import QPixmap
from qtpy.QtSql import QSqlQueryModel
from qtpy.QtWidgets import QWidget


class ImageDataModel(QSqlQueryModel):
    """
    A custom data model for handling image data stored in a database.
    This model detects columns containing image data and renders them as QPixmap objects.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the ImageDataModel.

        :param parent: The parent widget, if any.
        """
        super().__init__(parent)
        self._image_columns_checked: bool = False
        self._image_columns: set[int] = set()

    def _detect_image_columns(self) -> None:
        """
        Detect columns in the model that contain image data.
        """
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

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Optional[QPixmap]:
        """
        Retrieve data from the model, rendering image columns as QPixmap objects.

        :param index: The index of the data to retrieve.
        :param role: The role for which data is requested.
        :return: The data at the specified index and role.
        """
        if not self._image_columns_checked:
            self._detect_image_columns()
        col = index.column()

        if col in self._image_columns:
            if role in [Qt.DisplayRole, Qt.EditRole]:
                return None
            value = super().data(index, Qt.DisplayRole)
            if role == Qt.DecorationRole:
                if isinstance(value, QByteArray):
                    pixmap = QPixmap()
                    if pixmap.loadFromData(bytes(value)):
                        return pixmap
        return super().data(index, role)

    def get_data_at_index(self, row: int, name: str) -> Optional[Any]:
        """
        Retrieve data from a specific row and column name.

        :param row: The row index.
        :param name: The column name.
        :return: The data at the specified row and column.
        """
        record = self.record(row)
        variant = record.field(name).value()
        if not variant:
            column = record.indexOf(name)
            index = self.index(row, column)
            variant = super().data(index, Qt.ItemDataRole.DisplayRole)
        return variant

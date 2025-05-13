#!/usr/bin/env -S uv run --script
import sys
from pathlib import Path

from qtpy.QtCore import QCoreApplication
from qtpy.QtSql import QSqlDatabase, QSqlQuery

from sql_queries import QUERIES


def initialize_database():
    """Initialize the database connection."""
    db = QSqlDatabase.addDatabase("QSQLITE")  # Using SQLite as an example
    db.setDatabaseName("test.db")
    db.setConnectOptions("QSQLITE_ENABLE_DEBUG")
    if not db.open():
        print("Failed to connect to the database.")
        sys.exit(1)

    print("Database connection established.")
    return db


def run_query():
    query = QSqlQuery()
    if not query.exec(QUERIES["drop_table"]):
        raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")

    if not query.exec(QUERIES["new_db"]):
        raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")

    query = QSqlQuery()
    path = Path("Book.obj")
    mesh_blob = path.read_bytes()
    path = Path("BookTop.png")
    top_image_blob = path.read_bytes()
    path = Path("BookSide.png")
    side_image_blob = path.read_bytes()
    path = Path("BookFront.png")
    front_image_blob = path.read_bytes()
    path = Path("BookPersp.png")
    persp_image_blob = path.read_bytes()

    query.prepare("""INSERT INTO Meshes (name, mesh_data, mesh_type)
            VALUES(:name, :mesh_data, :mesh_type)""")
    query.bindValue(":name", "Test insert")
    query.bindValue(":mesh_data", mesh_blob)  # No need for QSql flags
    query.bindValue(":mesh_type", "obj")
    print(f"Mesh blob size: {len(mesh_blob)} bytes")
    if not query.exec():
        raise RuntimeError(f"Failed to execute query: {query.lastError().text()}")
    print(query.executedQuery())


def main():
    db = initialize_database()
    run_query()
    db.close()
    QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    main()
    # sys.exit(app.exec())

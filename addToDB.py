#!/usr/bin/env -S uv run --script

import argparse
import sqlite3
from sqlite3 import Error
import logging
from pathlib import Path
from dataclasses import dataclass


"""
Here I'm going to make the different elements a data class (think structure) it will make the code more
maintainable not need such a large function signature when passing the data around, we now only need to change in
one place
"""


@dataclass
class ClutterItem:
    """This is a data class for clutter items"""

    name: str
    mesh: str
    mesh_type: str
    top_image: str
    side_image: str
    front_image: str
    persp_image: str


class Connection:
    """
    Class to manage database connections and operations for the clutter base
    """

    def __init__(self, name: str):
        """Initialize the connection object note we don't connect here as we want to
        require the context manager to open and close the connection
        Parameters :
            name : str
                The name of the database file to connect to
        """
        self.name = name
        self.connection = None

    def _open(self):
        """
        Open the connection to the database internal method used with the context manager
        """
        try:
            self.connection = sqlite3.connect(self.name)
        except Error as e:
            print(f"Error connecting {e} with database {self.name}")

    def _close(self):
        """Close the connection to the database internal method used with the context manager"""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        """Enter the context manager"""
        self._open()
        return self

    def __exit__(self, *exc):
        """Exit the context manager"""
        self._close()

    def add_item(
        self,
        item: ClutterItem,
    ) -> None:
        """Add an item to the database
        Parameters :
            item : ClutterItem
            elements to add
        """
        try:
            logging.info(f"Adding item '{item.name}' to the database.")
            cursor = self.connection.cursor()
            query = """INSERT INTO Meshes (name, mesh_data, mesh_type, top_image, side_image, front_image, persp_image)
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""
            query_data = (
                item.name,
                self._load_blob(item.mesh),
                item.mesh_type,
                self._load_blob(item.top_image),
                self._load_blob(item.side_image),
                self._load_blob(item.front_image),
                self._load_blob(item.persp_image),
            )
            cursor.execute(query, query_data)
            self.connection.commit()
            logging.info(f"Item '{item.name}' added successfully.")
        except Exception as e:
            logging.error(f"Failed to add item '{item.name}' to the database: {e}")
            raise
        finally:
            cursor.close()

    def _load_blob(self, file_path: str) -> bytes:
        """Load the file as binary and return as the blob
        Parameters :
            file_path : str
                Path to the file to load as binary
        """
        if not file_path:
            logging.warning("File path is empty")
            return b""

        path = Path(file_path)
        if not path.is_file():
            logging.warning(f"File not found: {file_path}")
            return b""

        return path.read_bytes()


def add_mesh(database: str, item: ClutterItem) -> None:
    """Helper function to add a mesh to the database

    Parameters :
        database : str
            name of database to connect to.
        item : ClutterItem
            Elements to add
    """
    with Connection(database) as connection:
        connection.add_item(item)


if __name__ == "__main__":
    # parser arguments in the following format
    # Long flag, short flag help required
    parser_args = [
        ("--database", "-db", "Which DB to connect too", True),
        ("--mesh", "-m", "Path to the mesh to load", True),
        ("--name", "-n", "Name of the asset in the database", True),
        ("--type", "-t", "Mesh type must be obj, usd or fbx", True),
        ("--top", "-T", "Top Image", False),
        ("--side", "-s", "Side Image", False),
        ("--front", "-f", "Front Image", False),
        ("--persp", "-p", "Perspective Image", False),
    ]
    # create parser and add arguments
    parser = argparse.ArgumentParser(description="add mesh to database")

    for long_arg, short_arg, help_text, required in parser_args:
        parser.add_argument(long_arg, short_arg, help=help_text, required=required)

    args = parser.parse_args()
    item = ClutterItem(
        args.name,
        args.mesh,
        args.type,
        args.top,
        args.side,
        args.front,
        args.persp,
    )

    add_mesh(args.database, item)

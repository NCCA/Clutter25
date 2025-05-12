"""
Easy lookup for SQL tables.
"""

query_cols = "id,name,mesh_type,front_image,side_image,top_image,persp_image"
drop_table = "DROP TABLE IF EXISTS Meshes;"
new_db_sql = """Create table Meshes (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
mesh_data BLOB NOT NULL,
mesh_type TEXT CHECK(mesh_type IN('obj','usd','usdc','usdz','usda','fbx')),
top_image BLOB,
side_image BLOB,
front_image BLOB,
persp_image BLOB
);"""

delete_row = """DELETE FROM Meshes WHERE id=?"""
insert_new_item = """INSERT INTO Meshes (name, mesh_data, mesh_type, top_image, side_image, front_image, persp_image) VALUES (?, ?, ?, ?, ?, ?, ?)"""

"""This dictionary is used to map table names to their respective SQL queries."""

QUERIES = {
    "select_all": f"select {query_cols} from Meshes;",
    "drop_table": drop_table,
    "new_db": new_db_sql,
    "insert": insert_new_item,
    "delete_row": delete_row,
}

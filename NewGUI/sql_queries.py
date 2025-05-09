query_cols = "name,mesh_type,front_image,side_image,top_image,persp_image"
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

QUERIES = {"select_all": f"select {query_cols} from Meshes;", "drop_table": drop_table, "new_db": new_db_sql}

#!/usr/bin/env bash

# check we have a folder passed as a command line argument
if [ -z "$1" ]; then
    echo "Usage: $0 <folder>"
    exit 1
fi

echo "Generating Database"

sql="DROP TABLE IF EXISTS Meshes;
Create table Meshes (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
mesh_data BLOB NOT NULL,
mesh_type TEXT CHECK(mesh_type IN('obj','usd','usdc','usdz','usda','fbx')),
top_image BLOB,
side_image BLOB,
front_image BLOB,
persp_image BLOB
);"

echo $sql | sqlite3 ClutterTest.db


# Function to traverse directories and search for obj files
traverse_and_search() {
    local dir="$1"
    local obj_file=""
    local top_png=""
    local side_png=""
    local front_png=""
    local persp_png=""
    local name=""
    local type=""

    for file in "$dir"/*; do
        if [ -d "$file" ]; then
            traverse_and_search "$file"
        elif [ -f "$file" ]; then
            case "$file" in
                *.obj)
                    obj_file="$file"
                    type="obj"
                    basename="${obj_file##*/}"
                    name="${basename%.obj}"
                    ;;
                *Top*.png)
                    top_png="$file"
                    ;;
                *Side*.png)
                    side_png="$file"
                    ;;
                *Front*.png)
                    front_png="$file"
                    ;;
                *Persp*.png)
                    persp_png="$file"
                    ;;
            esac
        fi
    done

    if [ -n "$obj_file" ]; then
        echo "Adding $name $type $obj_file"
        ./addToDB.py -db ClutterTest.db --name "$name" --mesh "$obj_file" --type "$type" --top "$top_png" --side "$side_png" --front "$front_png" --persp "$persp_png"
    fi
}
# Start traversing from the current directory
traverse_and_search "$1"

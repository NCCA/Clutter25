#!/usr/bin/env bash

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

#./addToDB.py -db ClutterTest.db --name "utensils" --mesh "ExportedMeshes/utensils/utensils.obj" --type obj --top "ExportedMeshes/utensils/utensilsTop.png"

# Function to traverse directories and search for files
traverse_and_search() {
    local dir="$1"
    for file in "$dir"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, recursively call the function
            traverse_and_search "$file"
        elif [ -f "$file" ]; then
            # If it's a file, check its extension and content
            case "$file" in
                *.obj)
                    obj_file="$file"
                    ;;
                *.png)
                    if [[ "$file" == *Front* ]]; then
                        front_png="$file"
                    elif [[ "$file" == *Top* ]]; then
                        top_png="$file"
                    elif [[ "$file" == *Persp* ]]; then
                        persp_png="$file"
                    elif [[ "$file" == *Side* ]]; then
                        side_png="$file"
                    fi
                    # extract the extension as the type.
                    type="${obj_file##*.}"
                    basename="${obj_file##*/}"
                    # Extract the last part after the last '/'
                    name="${basename%.obj}"

                    ;;
            esac

        fi

    done
    echo "Adding $name $type $obj_file"
    ./addToDB.py -db ClutterTest.db --name $name --mesh $obj_file --type $type --top $top_png --side $side_png --front $front_png --persp $persp_png

}

# Start traversing from the current directory
traverse_and_search "$1"

# Clutter Base 25

This repo contains the main files used in the Pipeline and TD lab. I will update this readme when we add changes etc.

## Weds 30th April 25

I have modified the addToDB.py function we created in the lab to make it easier to maintain and updated to add the rest of the image files.

Key changes are using a [dataclass](https://docs.python.org/3/library/dataclasses.html) to make the function calls easier as I am only passing this.

Also added in all type hints and docstrings.

Updated the createDatabase.sh to add the rest of the image attributes to the database and to also automate adding all the sub folders to the database. This will allow all the exported meshes to be added to the database.

### TODO

next time we will start to create a stand alone GUI using PySide and load in the database and visualise it.

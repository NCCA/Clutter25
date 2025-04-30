# Clutter Base

A cross platform Mesh / asset library for storing and retriving small scene objects. 

1. Mesh data only for now not textures, shaders or look dev.
2. Store this with images of the finished model and a file format.

## What file formats to choose?

Support Obj, FBX and USD for file formats. 

What do we need to do with the mesh? 

1. scale and position at origin
2. make sure there is no extra material / lighting

# What attributes do we need to save?

Name Size Category  Description Front Side Top Perps [Face Count] File Type MeshData Version Data Author


| Attribute |  Data Type | Usage |
|-----------|------------|-------|
| ID        | int autoinc| Primary Key |
| Name      | VARCHAR  NotNULL  | We can use this for the main group in DCC |
| Category | Varchar | optional category |
| Description | VARCHAR Not Null | Description of item |
| MeshData    | BOB | the actual mesh <2Gb |
| MeshType    | Enum Obj,FBX,USD | what the format is |
| FrontImage  | Blob | front screen shot |
| SideImage  | Blob | Side screen shot |
| TopImage  | Blob | Top screen shot |
| PerspImage  | Blob | Persp screen shot |


# TODO / Plan

1. We need to get some data!
    - export mesh and screen shots
    - start to do this in a folder
2. Build database schema and connect to it
3. Write code to add data to database
4. Write GUI / Tools to add more 
5. Write Import GUI for Maya
6. Write Import GUI for Houdini
















from pathlib import Path
import os
import maya.cmds as cmds
import NCCA
import maya.OpenMaya as OM1 


def create_root_folder(root: str) -> Path:
    """
    Creates a root folder named 'ExportedMeshes' inside the specified directory.

    Args:
        root (str): The path to the directory where the 'ExportedMeshes' folder will be created.

    Returns:
        Path: A Path object representing the created 'ExportedMeshes' directory.
    """
    export_dir = Path(f"{root}/ExportedMeshes")
    export_dir.mkdir(exist_ok=True)
    return export_dir


def export_mesh(child : str, export_dir : Path) -> None :
    # create a folder for export
    # child is in the format |group name | top level group name |
    root_name = child.split("|")[2]
    export_path=export_dir/root_name
    export_path.mkdir(parents=True,exist_ok=True)
    group_name ="NCCA_Export_Group"
    if cmds.objExists(group_name) :
        cmds.delete(group_name)
    cmds.group(empty=True,world=True,name=group_name)
    cmds.showHidden(group_name)
    dup_name = cmds.duplicate(child,renameChildren=True)
    cmds.parent(dup_name,group_name)
    cmds.select(group_name)
    NCCA.center_pivot_to_bounding_box(group_name)
    NCCA.center_and_scale(group_name)
    NCCA.save_screenshots(export_path,250,250,root_name)
    cmds.file(f"{export_path}/{root_name}.obj",force=True,type="OBJexport",exportSelected=True)
    cmds.delete(group_name)


def export_selected_meshes(export_dir: Path) -> None:
    selected = cmds.ls(selection=True, long=True)
    if selected:
        child_groups = NCCA.get_child_groups(selected[0], depth=1)
        cmds.hide(all=True)
        interupter = OM1.MComputation()
        interupter.beginComputation()
        for child in child_groups :
            export_mesh(child,export_dir)
            if interupter.isInterruptRequested() :
                print("interuppted by user")
                interupter.endComputation()
                break
    else:
        print("No Groups Selected")
    cmds.showHidden(all=True)
    cmds.select(clear=True)
    print("Export Complete")


# recruse the groups and find each to level group

# export the file as obj

# export screenshots.

if __name__ == "__main__":
    try:
        root_folder = os.environ["CLUTTER_ROOT"]
        export_folder = create_root_folder(root_folder)
        export_selected_meshes(export_folder)
    except KeyError:
        print("CLUTTER_ROOT Not set")

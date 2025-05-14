import maya.api.OpenMaya as om
import maya.cmds as cmds


def get_selected_meshes():
    """Finds all selected meshes directly or within selected DAG paths."""
    selection = om.MGlobal.getActiveSelectionList()
    meshes = []

    for i in range(selection.length()):
        dag_path = selection.getDagPath(i)
        if dag_path.hasFn(om.MFn.kMesh):
            meshes.append(dag_path.partialPathName())  # Store mesh names
        else:
            meshes.extend(find_meshes(dag_path))

    return list(set(meshes))  # Remove duplicates


def find_meshes(dag_path):
    """Recursively finds all mesh nodes under the given DAG path."""
    meshes = []
    it = om.MItDag(om.MItDag.kDepthFirst)
    it.reset(dag_path, om.MItDag.kDepthFirst)

    while not it.isDone():
        child_path = it.getPath()
        if child_path.hasFn(om.MFn.kMesh):
            meshes.append(child_path.partialPathName())  # Store mesh names
        it.next()

    return meshes


def center_pivot_to_bounding_box(group_node):
    bbox = cmds.exactWorldBoundingBox(group_node)
    center = [
        (bbox[0] + bbox[3]) / 2,  # X center
        (bbox[1] + bbox[4]) / 2,  # Y center
        (bbox[2] + bbox[5]) / 2,
    ]  # Z center

    cmds.xform(group_node, pivots=center)  # Set pivot to bounding box center


def center_and_scale(group_node):
    """Moves the object to the origin and scales it to fit within a unit size (1x1x1)."""
    bbox = cmds.exactWorldBoundingBox(group_node)
    min_x, min_y, min_z, max_x, max_y, max_z = bbox

    # Compute center position
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0

    # Move object to origin
    cmds.move(-center_x, -center_y, -center_z, group_node, absolute=True)

    # Compute scaling factor for unit size
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z
    max_size = max(size_x, size_y, size_z)  # Largest dimension

    if max_size > 0:
        scale_factor = 1.0 / max_size
        cmds.scale(scale_factor, scale_factor, scale_factor, group_node, absolute=True)


def get_child_groups(parent_group, depth=1):
    """
    Get all child groups (transform nodes) under a selected group up to a specific depth.
    """
    selection_list = om.MSelectionList()
    selection_list.add(parent_group)
    dag_path = selection_list.getDagPath(0)

    # Create an iterator to go through the DAG
    it_dag = om.MItDag(om.MItDag.kDepthFirst)  # Traverse DepthFirst
    it_dag.reset(dag_path.node())

    child_groups = []

    while not it_dag.isDone():
        # Get the current item as a MFnDagNode
        fn_dag = om.MFnDagNode(it_dag.currentItem())

        # Get the current depth
        if (
            it_dag.depth() == depth
        ):  # depth=1 means the immediate children of the selected group
            child_groups.append(fn_dag.fullPathName())

        it_dag.next()

    return child_groups


def get_inclusive_matrix(obj_name, as_list=False):
    """
    Returns the inclusive (world) transformation matrix of the given Maya group as an MMatrix.
    as_list: If True, returns the matrix as a list of 16 elements. ideal for JSON serialization.
    """
    try:
        # Get the DAG path of the object
        selection_list = om.MSelectionList()
        selection_list.add(obj_name)
        dag_path = selection_list.getDagPath(0)

        # Get the inclusive matrix (world transformation matrix)
        inclusive_matrix = dag_path.inclusiveMatrix()
        if as_list:
            return [inclusive_matrix[i] for i in range(16)]
        else:
            return inclusive_matrix
    except Exception as e:
        print(f"Error: {e}")
        return None

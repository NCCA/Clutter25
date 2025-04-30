import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds
import pymel.core as pm


def save_screenshots(
    path: str,
    width: int,
    height: int,
    base_name: str,
    frame_all: bool = True,
    view_manip: bool = False,
    persp: bool = True,
    top: bool = True,
    side: bool = True,
    front: bool = True,
) -> None:
    # build a dictionary of views and their commands so we can use a loop
    views = {
        "Persp": ("cmds.viewSet(p=True, fit=True)", persp),
        "Top": ("cmds.viewSet(t=True, fit=True)", top),
        "Side": ("cmds.viewSet(s=True, fit=True)", side),
        "Front": ("cmds.viewSet(f=True, fit=True)", front),
    }

    for name, (command, is_active) in views.items():
        if is_active:
            try:
                # Set the active view
                exec(command)
                # Grab the view from Maya
                view = OpenMayaUI.M3dView.active3dView()
                # Set focus for the frame command
                panel = cmds.getPanel(visiblePanels=True)
                cmds.setFocus(panel[0])

                if frame_all:
                    pm.viewFit()
                
                # Dump to MImage
                image = OpenMaya.MImage()
                view.refresh()
                cmds.viewManip(v=view_manip)
                view.readColorBuffer(image, True)
                # Resize to selected size
                image.resize(width, height, preserveAspectRatio=True)
                # Write to file
                print(f"{path}/{base_name}{name}.png")
                image.writeToFile(f"{path}/{base_name}{name}.png", outputFormat="png")
            except Exception as e:
                print(f"Failed to save screenshot for {name} view: {e}")
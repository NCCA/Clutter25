# Maya Module (.mod) Files

A Maya module file is a simple text file with a .mod extension. It tells Maya where to find scripts, plugins, icons, and other resources. Module files are useful for organizing third-party or custom tools while keeping Maya’s environment clean.

## Location

Maya looks for .mod files in directories listed in the MAYA_MODULE_PATH environment variable. The common locations are:

Default Module Directories:
	•	Windows: C:\Users\YourUsername\Documents\maya\modules\
	•	Linux: ~/maya/modules/
    •	Mac: ~/Library/Preferences/Autodesk/maya/modules/
	•	Custom Paths: You can specify custom directories in MAYA_MODULE_PATH

These will be visible to all version of maya installed. It is also possible to create a module directory for a specific version of Maya. For example, you can create a directory named 2023 in the modules directory to store modules specific to Maya 2023.

We can check the current module path by running the following command in the script editor:

```python
import os
print(os.environ.get("MAYA_MODULE_PATH"))
```

## Mod file Syntax

The first line of the module file is always as follows:

```python
+ ModuleName version path/to/module
```

The + sign defines a module.
- ModuleName is the name of the tool/plugin.
- version is the module’s version number.
- path/to/module is the installation directory.

The rest of the file contains the paths to the resources. Here is an example of a module file:

```
+ ClutterBase 1.0 /Volumes/teaching/PipeLineAndTD/Clutter25
MAYA_PLUG_IN_PATH += plug-ins
scripts += /Volumes/teaching/PipeLineAndTD/Clutter25/scripts
PYTHONPATH += /Volumes/teaching/PipeLineAndTD/Clutter25/scripts
CLUTTER_ROOT = /Volumes/teaching/PipeLineAndTD/Clutter25
```

In this file we are setting the root project as ClutterBase then adding search paths for plugins, scripts and adding to the python path.

We can also define environment variables in the module file. In the example above, we are setting the CLUTTER_ROOT variable to the project root directory.

## Operators in Module Files

Maya module files support environment variable operations:

| Operator  | Meaning |
|-----------|---------|
| ```=``` | Sets the variable (overwrites existing values) |
| ```+=``` | Appends to the end of the existing variable (lower priority) |
| ```+:=``` | Appends to the beginning of the existing variable (higher priority) |


## Module API

We can list the modules using the following

```python
cmds.moduleInfo(listModules=True)
```

We can get more info using 

```python
name="ClutterBase"
print(cmds.moduleInfo(definition=True, moduleName=name))
print(cmds.moduleInfo(path=True, moduleName=name))
print(cmds.moduleInfo(version=True, moduleName=name))
/Users/jmacey/Library/Preferences/Autodesk/maya/modules/ClutterBase.mod
/Volumes/teaching/PipeLineAndTD/Clutter25
1.0
```

When Maya starts up it loads all of the module files it finds, making the module's plug-ins, scripts and other resources available for use. Note that the plug-ins themselves are not loaded at this time, Maya is simply made aware of them so that they can be loaded if needed.

The loadModule command provides the ability to list and load any new modules which have been added since Maya started up, thereby avoiding the need to restart Maya before being able to use them. 

```python
import maya.cmds as cmds
name="ClutterBase"
cmds.loadModule(scan=True)
cmds.loadModule(load=name)
cmds.loadModule(allModules=True)
```

Note that this doesn't seem to update any of the environment variables, so if you have added new paths to the module file you will need to restart Maya to pick up the changes.

## Module installer script

The following is a simple module installer script.

```python
#!/usr/bin/env -S uv run --script

import argparse
import os
import platform
import sys
from pathlib import Path

maya_locations = {
    "Linux": "/maya/",
    "Darwin": "/Library/Preferences/Autodesk/maya",
    "Windows": "\\Documents\\maya\\",
}

MODULE_NAME = "ClutterBase"
VERSION = "1.0"
PYTHON_PATHS="scripts"

def install_module(location, os):
    print(f"installing to {location}")
    # first write the module file
    current_dir = Path.cwd()
    # if the module folder doesn't exist make it
    module_dir = Path(location + "//modules")
    module_path = location + f"//modules/{MODULE_NAME}.mod"
    ## change to \\ for windows (easier then messing with Path objects)
    if os == "Windows":
        module_dir = Path(location + "\\modules")
        module_path = location + "modules\\{MODULE_NAME}.mod"
    module_dir.mkdir(exist_ok=True)

    if not Path(module_path).is_file():
        print("writing module file")
        with open(module_path, "w") as file:
            # Firs write out the module name and version with location
            file.write(f"+ {MODULE_NAME} {VERSION} {current_dir}\n")
            # we use += to append to the existing paths if it is
            # +:= Operator we appending with Higher Priority (pre-pend)
            file.write(f"MAYA_PLUG_IN_PATH += {current_dir}/plug-ins\n")
            file.write(f"scripts += {current_dir}/{PYTHON_PATHS}\n")
            file.write(f"PYTHONPATH += {current_dir}/{PYTHON_PATHS}\n")
            # Going to set some test ENVARS 
            file.write(f"CLUTTER_ROOT = {current_dir}\n")
    
            
def check_maya_installed(op_sys):
    mloc = f"{Path.home()}{maya_locations.get(op_sys)}"
    if not os.path.isdir(mloc):
        raise
    return mloc


if __name__ == "__main__":

    try:
        op_sys=platform.system()
        m_loc = check_maya_installed(op_sys)
    except:
        print("Error can't find maya install")
        sys.exit(-1)

    install_module(m_loc, op_sys)
```
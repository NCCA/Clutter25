from qtpy.Qt3DCore import QEntity, QTransform
from qtpy.Qt3DExtras import QFirstPersonCameraController, QMetalRoughMaterial, Qt3DWindow
from qtpy.Qt3DRender import QMesh
from qtpy.QtCore import Qt, QUrl
from qtpy.QtGui import QVector3D
from qtpy.QtWidgets import QVBoxLayout, QWidget


class ModelViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        layout = QVBoxLayout(self)

        # Create the 3D window
        self.view = Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(Qt.gray)  # Set background to black

        # Root entity
        root_entity = QEntity()

        mesh = QMesh()
        mesh.setSource(QUrl.fromLocalFile("Helix.obj"))

        material = QMetalRoughMaterial()
        transform = QTransform()
        transform.setScale(1.0)
        transform.setTranslation(QVector3D(0, 0, 0))
        mesh_entity = QEntity(root_entity)

        mesh_entity.addComponent(mesh)
        mesh_entity.addComponent(material)
        mesh_entity.addComponent(transform)

        # Setup camera
        camera = self.view.camera()
        camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000)
        camera.setPosition(QVector3D(0, 0, 2))
        camera.setViewCenter(QVector3D(0, 0, 0))

        # Add camera controls
        # controller = QOrbitCameraController(root_entity)
        controller = QFirstPersonCameraController(root_entity)
        controller.setCamera(camera)
        # Finalize scene
        self.view.setRootEntity(root_entity)

        # Wrap the Qt3DWindow in a container
        container = self.createWindowContainer(self.view, self)
        container.setMinimumSize(400, 300)  # Set a minimum size for the container
        container.setFocusPolicy(Qt.StrongFocus)  # Ensure the container can receive focus
        layout.addWidget(container)
        self.resize(800, 600)

        # Debugging
        print("Qt3DWindow created:", self.view)
        print("Container size:", container.size())
        print("Container focus policy:", container.focusPolicy())

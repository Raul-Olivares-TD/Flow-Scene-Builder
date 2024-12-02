import hou
from PySide2 import QtWidgets, QtCore
import shotgun_api3


class AssetsUI(QtWidgets.QWidget):
    def __init__(self, scene_data):
        super().__init__()
        self.scene_data = scene_data
        self.flow = FlowConnection(SceneData())
        self.main_layout()

    def main_layout(self):
        # Main layout
        main_lyt = QtWidgets.QVBoxLayout()
        # Set the layout to himself
        self.setLayout(main_lyt)

        #############
        # GROUP BOX #
        #############
        # Box layout to represents the group box content
        box_lyt = QtWidgets.QHBoxLayout()
        # Add the data layout to the main layout
        main_lyt.addLayout(box_lyt)
        # Instance the SceneData to gets the project data
        scene_data = self.scene_data.data_from_houdini()

        # Generates the title and content for the groupbox
        for k, v in scene_data.items():
            group = self.group_box(k, v)
            box_lyt.addWidget(group)

        ###############
        # ASSETS LIST #
        ###############
        # Assets list layout
        assets_list_lyt = QtWidgets.QVBoxLayout()
        # Add Assets list layout to the main layout
        main_lyt.addLayout(assets_list_lyt)
        # Send the layout to the assets list
        self.assets_list(assets_list_lyt)

    def group_box(self, title, content):
        """ Creates the group box

        :param title: Get the title generate at the main layout
        :param content: Get the content generate at the main layout
        :return: A group box widget with title and content
        :rtype: QtWidget.QGroupBox()
        """
        # Group box
        grp = QtWidgets.QGroupBox(title)
        # Group box vertical layout
        grp_lyt = QtWidgets.QVBoxLayout()
        # Set the group layout
        grp.setLayout(grp_lyt)

        # Label with the content
        label = QtWidgets.QLabel(content)

        # Add the widgets at the group box layout
        grp_lyt.addWidget(label, alignment=QtCore.Qt.AlignCenter)

        return grp

    def assets_list(self, layout):
        # Assets list
        assets_list = QtWidgets.QListWidget()
        assets_list.addItems(self.flow.assets_from_shot())
        layout.addWidget(assets_list)


class SceneData:
    def data_from_houdini(self):
        """ Extract data from Houdini scene filename.

        :return: A dictionary with the data of the project for the groupbox
        :rtype: dict
        """
        # Get the name of the scene
        scene = hou.hipFile.basename()
        # Split by a "." to exclude the ext of the file and get the basename
        basename = scene.split(".")[0]
        # Gets a list of all the data names at the project at the basename
        names_list = basename.split("_")
        # Dict with the title and the data names for the groupbox
        path_data = {
            "Project": names_list[0],
            "Sequence": names_list[1],
            "Shot": f"{names_list[2]}_{names_list[3]}",
            "Task": names_list[4],
        }

        return path_data


class FlowConnection:
    def __init__(self, scene_data):
        """ Authentication for access to flow data."""
        self.sg = shotgun_api3.Shotgun(
            "https://dramastudio.shotgrid.autodesk.com/",
            script_name="tdscript",
            api_key="rkmbtqY#7tjjxtxplsbvodaaq")

        self.scene_data = scene_data

    def assets_from_shot(self):
        """ Getting the assets from flow using the shot data from houdini hip file.

        :return: A list with the assets at the shot
        :rtype: list
        """
        shot = self.scene_data.data_from_houdini()["Shot"]

        filters = [
            ["code", "is", shot]
        ]

        shot_data = self.sg.find("Shot", filters, fields=["assets"])

        assets_list = []
        for data in shot_data:
            assets = data["assets"]
            for asset in assets:
                assets_list.append(asset["name"])

        return assets_list


w = AssetsUI(SceneData())
w.show()

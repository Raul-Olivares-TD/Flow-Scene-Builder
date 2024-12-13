import driveDownload
import hou
import json
import jsonFlow
from PySide2 import QtWidgets, QtCore
import shotgun_api3


class AssetsUI(QtWidgets.QWidget):
    # Signal to send the check assets to verify the versions
    check_assets_signal = QtCore.Signal(list)
    # Signal to notify when approved versions are ready
    assets_ready_signal = QtCore.Signal(list)
    # Signal with the assets path
    assets_path_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.scene_data = SceneData()
        self.flow = FlowConnection()
        self.down = DownloadImportAssets()

        # Connect signals
        self.check_assets_signal.connect(self.flow.assets_id)
        self.assets_ready_signal.connect(self.down.drive_files_id)
        self.assets_path_signal.connect(self.down.download_assets_dialog)

        self.main_layout()

        # Apply Houdini stylesheet
        self.setStyleSheet(hou.qt.styleSheet())


    def main_layout(self):
        """ Creates the elements of the UI."""
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
        for title, content in scene_data.items():
            group = self.group_box(title, content)
            box_lyt.addWidget(group)

        ###############
        # ASSETS LIST #
        ###############
        # Assets list layout
        assets_lyt = QtWidgets.QVBoxLayout()
        # Add Assets list layout to the main layout
        main_lyt.addLayout(assets_lyt)
        # Send the layout to the assets list
        self.assets_list(assets_lyt)

        ####################
        # ASSETS SAVE PATH #
        ####################
        # Layout for the assets path
        path_lyt = QtWidgets.QHBoxLayout()
        # Label
        assets_label = QtWidgets.QLabel("Assets Path")
        # Line Edit Path
        hip = hou.getenv("HIP")
        self.assets_path = QtWidgets.QLineEdit(f"{hip}/")
        self.check_assets_path()
        # Dialog button
        dialog_button = QtWidgets.QToolButton()
        # Icon Dir
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)
        # Set the icon
        dialog_button.setIcon(icon)
        # Emit signal to open a dialog
        dialog_button.clicked.connect(self.dialog_assets_directory)
        # Add the layout to the main layout
        main_lyt.addLayout(path_lyt)
        # Add widgets to the asset path layout
        path_lyt.addWidget(assets_label, alignment=QtCore.Qt.AlignCenter)
        path_lyt.addWidget(self.assets_path)
        path_lyt.addWidget(dialog_button)

        ###################
        # IMPORTER BUTTON #
        ###################
        # Importer button
        imp_btn = QtWidgets.QPushButton("IMPORT ASSETS TO SCENE")
        # Signal
        imp_btn.clicked.connect(self.checked_assets)
        # Add button to the main layout
        main_lyt.addWidget(imp_btn)

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
        """ Creates a list with the assets at the shot and create a checbox
            for select the assets.

        :param layout: Contains the layout for the QListWidget assets
        """
        # Assets QList
        self.assets = QtWidgets.QListWidget()
        # Add the QList at the layout
        layout.addWidget(self.assets)
        # Create the checkboxes to the items at the list
        for asset in self.flow.assets_from_shot():
            # Create each asset like a new item to add at the QList
            list_item = QtWidgets.QListWidgetItem(asset)
            # Enable checkbox
            list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            # Sets the initial state to the checkbox to unchecked
            list_item.setCheckState(QtCore.Qt.Unchecked)
            # Add the items to the QList
            self.assets.addItem(list_item)

    def dialog_assets_directory(self):
        """ Alternative window that allows select any directory on the pc."""
        # Create the dialog
        path = QtWidgets.QFileDialog.getExistingDirectory(
            # Parent at the same window
            self,
            # Set window title
            "Select Custom Path",
            # Disk search by default
            "C:"

        )

        # Creates the path with the dialog directory
        if path == "":
            self.path.setText("")
        elif len(path) == 3:
            rep_path = path.replace("/", "")
            self.assets_path.setText(f"{rep_path}/")

        else:
            self.assets_path.setText(f"{path}/")

    def check_assets_path(self):
        """ Correcting the default path to save the download assets."""
        # Split assets path
        assets_path = self.assets_path.text().split("/")

        # Compare if scenes exists at assets path and modify by assets
        if "scenes" in assets_path:
            update_path = self.assets_path.text().replace("scenes", "assets")
            self.assets_path.setText(update_path)

    def checked_assets(self):
        """ Create a list with the checked assets

        :return: A list with items selected
        :rtype: list
        """
        # Create a list with the checked assets at the list
        items = [self.assets.item(i).text() for i in range(self.assets.count())
                      if self.assets.item(i).checkState() == QtCore.Qt.Checked]

        if not items:
            QtWidgets.QMessageBox.warning(self, "Warning", "No assets selected!")
            return

        # Emit signal to process checked assets
        self.check_assets_signal.emit(items)
        # Get approved versions and emit the ready signal
        approved_versions = self.flow.approved_versions()
        # Emit the approved versions
        self.assets_ready_signal.emit(approved_versions)
        # Get the assets path
        assets_path = f"{self.assets_path.text()}"
        # Emit the assets path signal
        self.assets_path_signal.emit(assets_path)
        # Close the window
        self.close()


class SceneData:
    def data_from_houdini(self):
        """ Extract data from Houdini scene filename.

        :return: A dictionary with the data of the project for the groupbox
        :rtype: dict
        """
        # Get the name of the scene
        scene_basename = hou.hipFile.basename()
        # Split by a "." to exclude the ext of the file and get the basename
        basename = scene_basename.split(".")[0]
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
    def __init__(self):
        super().__init__()
        """ Authentication for access to flow data."""
        self.sg = shotgun_api3.Shotgun(
            "https://dramastudio.shotgrid.autodesk.com/",
            script_name="tdscript",
            api_key="rkmbtqY#7tjjxtxplsbvodaaq")

        self.scene_data = SceneData()
        self.down = DownloadImportAssets()
        self.asset_ids = None

    def get_project_id(self):
        project = self.scene_data.data_from_houdini()["Project"]

        filters = [
            ["name", "is", project]
        ]

        project_data = self.sg.find("Project", filters, fields=["id"])

        project_id = None
        for data in project_data:
            project_id = data["id"]

        return project_id

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

        assets_list = [asset["name"] for data in shot_data
                       for asset in data["assets"]]

        return assets_list

    def assets_id(self, checked_assets):
        """ Getting the id of the checked assets"""
        # Find the assets corresponding to the names provided
        asset_filters = [
            ["project", "is", {"type": "Project", "id": self.get_project_id()}],
            ["code", "in", checked_assets]  # Busca por nombre de asset
        ]

        # Getting the name and id of each asset
        asset_fields = ["id", "code", "sg_asset_type"]
        # Request to find the assets needed
        assets = self.sg.find("Asset", asset_filters, asset_fields)

        # Gets the id of the obtained assets
        self.asset_ids = [{"type": "Asset", "id": asset["id"]}
                          for asset in assets]

    def approved_versions(self):
        """ Getting the approved versions of each asset selected.

        :return: A list with a dict with the version of each asset at the shot
        :rtype: list
        """
        # Searching for approved versions related to those assets
        version_filters = [
            ["project", "is", {"type": "Project", "id": self.get_project_id()}],
            ["entity", "in", self.asset_ids],
            ["sg_status_list", "is", "apr"]
        ]

        # Getting the name and the path of each asset version
        version_fields = ["code", "sg_path_to_geometry"]
        # Request to find the versions needed
        versions = self.sg.find("Version", version_filters, version_fields)

        return versions


class DownloadThread(QtCore.QThread):
    # Signal to update the progress bar
    progress = QtCore.Signal(int)
    # Signal to update the file name in the interface
    file_name = QtCore.Signal(str)
    # Signal to notify that the download has finished
    download_complete = QtCore.Signal()
    # Signal to notify that the download has been cancelled
    download_canceled = QtCore.Signal()


    def __init__(self, files_id, directory_path):
        super().__init__()
        self.files_id = files_id
        self.directory_path = directory_path
        # Indicator to cancel download
        self.cancel_requested = False
        self.downloaded_files = []

    def run(self):
        for file_id in self.files_id:
            if self.cancel_requested:
                self.download_canceled.emit()
                return  # Exit the `run` method to stop the thread from running

            try:
                driveDownload.download_files(
                    [file_id],
                    self.directory_path,
                    self.progress.emit,
                    lambda file_name: self.list_file_name(file_name),
                    # Access to cancel request at any time with the lambda function
                    lambda: self.cancel_requested,

                )
            except Exception as e:
                print(f"An error occurred while downloading file {file_id}: {e}")
                continue

        self.download_complete.emit()

    def cancel_download(self):
        """ Method to request cancellation of download."""
        self.cancel_requested = True

    def list_file_name(self, file_name):
        """ Stores the name of the downloaded file."""
        self.downloaded_files.append(file_name)
        self.file_name.emit(file_name)


class DownloadImportAssets:
    def drive_files_id(self, approved_versions):
        """ Generates the id for download the Google Drive files.

        :return:
        """
        self.files_id = []
        for version in approved_versions:
            drive_link = version["sg_path_to_geometry"]
            file_id = drive_link.split("/")[-2]
            self.files_id.append(file_id)

    def download_assets_dialog(self, assets_path):
        """ Dialog with the download process in a second thread."""
        # Dialog Widget
        self.download_dlg = QtWidgets.QDialog()
        # Dialog layout
        download_dlg_lyt = QtWidgets.QVBoxLayout()
        # Download Title
        self.download_text = QtWidgets.QLabel("Download Asset:")
        # Align title
        self.download_text.setAlignment(QtCore.Qt.AlignCenter)
        # Progress bar widget
        self.dlg_bar = QtWidgets.QProgressBar()
        # Align progress bar
        self.dlg_bar.setAlignment(QtCore.Qt.AlignCenter)
        # Button for cancel download
        self.cancel_btn = QtWidgets.QPushButton("Cancel Download")
        # Signal when button clicked
        self.cancel_btn.clicked.connect(self.cancel_download)
        # Set the layout at the dialog
        self.download_dlg.setLayout(download_dlg_lyt)
        # Add the elements to the dialog layout
        download_dlg_lyt.addWidget(self.download_text)
        download_dlg_lyt.addWidget(self.dlg_bar)
        download_dlg_lyt.addWidget(self.cancel_btn)
        # Testing
        self.assets_path = assets_path
        # Second threat download call
        self.thread = DownloadThread(self.files_id, self.assets_path)
        # Connect progress bar signal with function update progress bar
        self.thread.progress.connect(self.update_progress_bar)
        # Connect file name signal with function to show the name at the text
        self.thread.file_name.connect(self.update_asset_text)
        # Connect complete signal
        self.thread.download_complete.connect(self.files_download_list)
        self.thread.download_complete.connect(self.download_finished)

        # Start the download thread
        self.thread.start()

        # Apply the Houdini stylesheet at the dialog
        self.download_dlg.setStyleSheet(hou.qt.styleSheet())
        # Exec the dialog
        self.download_dlg.exec_()

    def update_progress_bar(self, value):
        """ Uptdate the value of the progress bar."""
        self.dlg_bar.setValue(value)

    def update_asset_text(self, value):
        """ Show the name of the files in the dialog."""
        self.download_text.setText(f"Download Asset: {value}")

    def cancel_download(self):
        """ Call the cancel download."""
        # Call the method for cancel download
        self.thread.cancel_download()
        # Close the dialog after cancel
        self.download_dlg.close()
        # Show a message that the download is canceled
        hou.ui.displayMessage("Download Cancel")

    def download_finished(self):
        """ Closes the download dialog, shows a completion message
            and call for imports assets into the scene.
        """
        # Close dialog after finish
        self.download_dlg.close()
        # Show where the files saved
        hou.ui.displayMessage("Files download")
        self.import_assets_to_houdini()

    def files_download_list(self):
        """ Convert the list of the files in a set because the list
            updates with each chunk and the file repeats.
        :return: A set with all the files downloaded
        :rtype: set
        """
        files_set = set(self.thread.downloaded_files)

        return files_set

    def get_json_tasks(self):
        """ Read the json file in the user disk.

        :return: A dictionary with all the data form Flow.
        :rtype: dict
        """
        # Path with json file
        json_file = jsonFlow.JsonFlowData().create_path()
        # Reading the file and convert to python dict
        with open(json_file, "r") as f:
            json_data = json.load(f)

        return json_data

    def import_assets_to_houdini(self):
        """ Import the assets selected in the import assets list
            into the scene.
        """
        # Get the assets data from json
        json_assets = self.get_json_tasks()["Assets"]
        # Obj Path
        obj = hou.node("/obj")
        # Creates a geometry node in obj
        geo = obj.createNode("geo", "assets")
        # Set the position of the node in the network
        geo.setPosition((0, -1))
        # Creates a merge node inside the geometry node
        merge = geo.createNode("merge")

        # Get each file in the files download list
        for file in self.files_download_list():
            # Gets the name of the file
            name = file.split(".")[0]
            # Gets the extension of the file
            ext = file.split(".")[1]

            # Get each asset at the json
            for asset in json_assets:
                if name in asset["code"]:
                    # Check the extension for correct way to import assets
                    if ext == "abc":
                        # If the asset is a camera
                        if asset["sg_asset_type"] == "Camera":
                            null = obj.createNode("null")
                            null.parm("scale").set(0.01)
                            abc_arch = null.createOutputNode("alembicarchive",
                                       name)
                            abc_arch.parm("fileName").set(
                            f"{self.assets_path}{name}.{ext}")
                            abc_arch.parm("buildHierarchy").pressButton()
                            abc_arch.setPosition((0, -3))

                        # If the assets is an alembic but isn't a camera
                        else:
                            abc_file = geo.createNode("alembic", name)
                            abc_file.parm("fileName").set(
                                f"{self.assets_path}{name}.{ext}")
                            unpack = abc_file.createOutputNode("unpack")
                            convert = unpack.createOutputNode("convert")
                            transform = convert.createOutputNode("xform")
                            transform.parm("scale").set(0.01)
                            null = transform.createOutputNode("null",
                                                              f"OUT_{name.upper()}")
                            merge.setNextInput(null)

                    # Check the extension for correct way to import assets
                    elif ext == "fbx":
                        # If the asset is a character or creature
                        if (asset["sg_asset_type"] == "Creature"
                                or asset["sg_asset_type"] == "Character"):
                            fbx_char = geo.createNode("fbxcharacterimport")
                            fbx_char.parm("fbxfile").set(f"{self.assets_path}"
                                                         f"{name}.{ext}")
                            null = fbx_char.createOutputNode("null",
                                                             f"OUT_{name.upper()}")
                            merge.setNextInput(null)

                        # If the asset haven't skeleton
                        else:
                            fbx_file = geo.createNode("file")
                            fbx_file.parm("file").set(f"{self.assets_path}"
                                                      f"{name}.{ext}")
                            transform = fbx_file.createOutputNode("xform")
                            transform.parm("scale").set(0.01)
                            null = transform.createOutputNode("null",
                                                              f"OUT_{name.upper()}")
                            merge.setNextInput(null)

                    # Assets that isn't abc or fbx and need a file node to import
                    else:
                        file = geo.createNode("file")
                        file.parm("file").set(f"{self.assets_path}"
                                              f"{name}.{ext}")
                        transform = file.createOutputNode("xform")
                        transform.parm("scale").set(0.01)
                        null = transform.createOutputNode("null",
                                                          f"OUT_{name.upper()}")
                        merge.setNextInput(null)

        # Sort the nodes
        obj.layoutChildren()
        geo.layoutChildren()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = AssetsUI()
    w.show()
    app.exec_()
else:
    w = AssetsUI()
    w.show()

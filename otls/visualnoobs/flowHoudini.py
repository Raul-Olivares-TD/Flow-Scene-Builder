import driveDownload
import hou
import json
import jsonFlow
import os
from PySide2 import QtWidgets, QtCore, QtGui
import psutil
import webbrowser


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
        """Método para solicitar la cancelación de la descarga."""
        self.cancel_requested = True

    def list_file_name(self, file_name):
        """Almacena el nombre del archivo descargado."""
        self.downloaded_files.append(file_name)
        self.file_name.emit(file_name)


class SceneBuilder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.build_layouts()
        self.user_data_layout()
        self.create_table()
        self.notes_assets_layouts()
        self.save_path_layouts()
        self.scene_load_layout()
        self.build_tasks()

        # Apply the Houdini stylesheet.
        self.setStyleSheet(hou.qt.styleSheet())

    def build_layouts(self):
        """ Creates the layouts necessary to the UI."""
        # CREATES LAYOUTS
        # Main layout
        self.main_lyt = QtWidgets.QVBoxLayout()
        # Horizontal layout
        self.hor_lyt = QtWidgets.QHBoxLayout()
        # Table layout
        self.table_lyt = QtWidgets.QVBoxLayout()
        # Btn layout
        self.btn_lyt = QtWidgets.QVBoxLayout()
        # Grid layout
        self.grid_lyt = QtWidgets.QGridLayout()
        # Asset buttons layout
        self.assets_btn = QtWidgets.QVBoxLayout()
        # Web buttons layout
        self.web_btn = QtWidgets.QVBoxLayout()
        # Separator
        self.sep = QtWidgets.QFrame()
        self.sep.setFrameShape(QtWidgets.QFrame.HLine)

        # Set the main layout to myself
        self.setLayout(self.main_lyt)
        # Set the horizontal lyt for these elements
        self.main_lyt.addLayout(self.hor_lyt)
        self.main_lyt.addWidget(self.sep)
        # Set the table at the main lyt
        self.main_lyt.addLayout(self.table_lyt)
        # Set the assets and notes elements at the layout
        self.main_lyt.addLayout(self.grid_lyt)
        # Button Load scene
        self.main_lyt.addLayout(self.btn_lyt)

    def user_data_layout(self):
        """ Creates the user data elements."""
        # Label: Show the User title
        user_label = QtWidgets.QLabel("User: ")

        # Label: Show the Flow user email
        user = QtWidgets.QLabel()
        user.setText(os.environ["FLOW_USER"])

        # UPDATE BUTTON
        # Button: Update tasks, exec functions and creates the table
        update_btn = QtWidgets.QPushButton("Update Data Flow")
        update_btn.clicked.connect(self.exec_functions)
        update_btn.clicked.connect(self.get_json_tasks)
        update_btn.clicked.connect(self.create_table)

        # ADD ELEMENTS TO THE LAYOUTS
        self.hor_lyt.addWidget(user_label)
        self.hor_lyt.addWidget(user)
        self.hor_lyt.addWidget(update_btn)

    def create_table(self):
        """ Create a table with all the tasks assigned only to the user, obtaining
            this data directly from Flow.
        """
        try:
            # Table
            self.table = QtWidgets.QTableWidget()
            # Creates Columns and Rows
            self.table.setColumnCount(len(self.build_tasks()))
            self.table.setRowCount(len(self.build_tasks()[0]))
            # Table Headers
            self.table_headers = ["Sequences", "Shots", "Project", "Department",
                                  "Task", "Status",
                                  "Priority", "Start Date", "End Date",
                                  "Description"]
            # Table Headers
            self.table.setHorizontalHeaderLabels(self.table_headers)

            # Table Items
            for col, lista in enumerate(self.build_tasks()):
                for row, item in enumerate(lista):
                    self.table.setItem(row, col, QtWidgets.QTableWidgetItem(item))

            # Set table data and settings
            self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.table.setShowGrid(False)
            self.table.verticalHeader().setVisible(False)
            self.table.setShowGrid(False)
            # Signal to get info when select one row/column
            self.table.currentCellChanged.connect(self.create_scene_path)
            self.table.currentCellChanged.connect(self.change_cheks)
            self.table_lyt.addWidget(self.table)

        except:
            # Text Update Data Flow
            self.text_update = QtWidgets.QTextEdit()
            self.text_update.setText("UPDATE THE DATA FLOW FOR VIEW THE TABLE")
            self.text_update.setAlignment(QtCore.Qt.AlignCenter)
            # Modify the font size
            font = self.text_update.font()
            font.setPointSize(38)
            self.text_update.setFont(font)
            self.table_lyt.addWidget(self.text_update)

    def notes_assets_layouts(self):
        """ Creates the notes and assets elements."""
        # NOTES DATA
        # Checkbox: Allows to show the notes
        self.check_notes = QtWidgets.QCheckBox("View Notes")
        self.check_notes.stateChanged.connect(self.notes)
        # Text: Show the notes in a text
        self.notes_text = QtWidgets.QTextEdit()
        self.notes_text.setReadOnly(True)

        # ASSETS DATA
        # Checkbox: Allows to show the assets
        self.assets_check = QtWidgets.QCheckBox("Get Assets")
        self.assets_check.stateChanged.connect(self.get_assets)

        # Assets lists: Show the assets at the shot
        self.assets_list = QtWidgets.QListWidget()
        self.assets_list.setDragEnabled(True)
        self.assets_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.assets_list.itemSelectionChanged.connect(self.assets_to_import)

        # Tool Button: Button to move items
        self.btn_move = QtWidgets.QToolButton()
        right_arrow = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_ArrowRight)
        self.btn_move.setIcon(right_arrow)
        self.btn_move.clicked.connect(self.assets_move)

        # Tool Button: Button to delete items
        self.btn_delete = QtWidgets.QToolButton()
        delete_icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_TrashIcon)
        self.btn_delete.setIcon(delete_icon)
        self.btn_delete.clicked.connect(self.asset_delete)

        # Label: Assets to import title
        txt_assets_to_import = QtWidgets.QLabel("Assets to import")

        # List: Assets list that will be imported in the scene
        self.import_assets_list = QtWidgets.QListWidget()
        self.import_assets_list.setAcceptDrops(True)
        self.import_assets_list.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.import_assets_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.import_assets_list.itemSelectionChanged.connect(self.assets_to_remove)

        # GitHub Button
        username = os.environ["USERNAME"]
        github_img_path = (f"C:/Users/{username}/Documents/houdini20.5/otls"
                           f"/visualnoobs/img/github_logo_w.png")
        github_btn = QtWidgets.QToolButton()
        github_icon = QtGui.QIcon(github_img_path)
        github_btn.setIcon(github_icon)
        github_btn.clicked.connect(self.web_github)

        # Linkedin Button
        linkedin_img_path = (f"C:/Users/{username}/Documents/houdini20.5"
                             f"/otls/visualnoobs/img/linkedin_logo_w.png")
        linkedin_btn = QtWidgets.QToolButton()
        linkedin_icon = QtGui.QIcon(linkedin_img_path)
        linkedin_btn.setIcon(linkedin_icon)
        linkedin_btn.clicked.connect(self.web_linkedin)

        # ADD ELEMENTS TO THE LAYOUTS
        # Horizontal layout
        self.assets_btn.addWidget(self.btn_move)
        self.assets_btn.addWidget(self.btn_delete)
        self.web_btn.addWidget(github_btn)
        self.web_btn.addWidget(linkedin_btn)
        # QGrid Layout
        self.grid_lyt.addWidget(self.check_notes, 1, 0)
        self.grid_lyt.addWidget(self.assets_check, 1, 1)
        self.grid_lyt.addWidget(txt_assets_to_import, 1, 3)
        self.grid_lyt.addWidget(self.notes_text, 2, 0)
        self.grid_lyt.addWidget(self.assets_list, 2, 1)
        self.grid_lyt.addLayout(self.assets_btn, 2, 2,
                                alignment=QtCore.Qt.AlignCenter)
        self.grid_lyt.addWidget(self.import_assets_list, 2, 3)
        self.grid_lyt.addLayout(self.web_btn, 2, 4,
                                alignment=QtCore.Qt.AlignCenter)

    def save_path_layouts(self):
        """ Creates the path elements."""
        # SCENE PATH
        # Disks Group: Wraps the device section of the menu
        disks_group = QtWidgets.QGroupBox("Device")
        disks_group_lyt = QtWidgets.QVBoxLayout()
        disks_group.setLayout(disks_group_lyt)

        # Menu disks: Menu with all the device in the pc
        self.menu_disks = QtWidgets.QComboBox()
        # self.menu_disks.addItem("")
        self.menu_disks.addItems(self.detect_disks())
        disks_group_lyt.addWidget(self.menu_disks)
        self.menu_disks.currentTextChanged.connect(self.create_scene_path)

        # Project Group: Show the project name selected at the table
        project_group = QtWidgets.QGroupBox("Project")
        self.project_group_lyt = QtWidgets.QVBoxLayout()
        project_group.setLayout(self.project_group_lyt)
        self.project_group_label = QtWidgets.QLabel()

        # Sequence Group: Show the sequence name selected at the table
        seq_group = QtWidgets.QGroupBox("Sequence")
        self.seq_group_lyt = QtWidgets.QVBoxLayout()
        seq_group.setLayout(self.seq_group_lyt)
        self.seq_group_label = QtWidgets.QLabel()

        # Shot Group: Show the shot name selected at the table
        shot_group = QtWidgets.QGroupBox("Shot")
        self.shot_group_lyt = QtWidgets.QVBoxLayout()
        shot_group.setLayout(self.shot_group_lyt)
        self.shot_group_label = QtWidgets.QLabel()

        # Task group: Show the task name selected at the table
        task_group = QtWidgets.QGroupBox("Task")
        self.task_group_lyt = QtWidgets.QVBoxLayout()
        task_group.setLayout(self.task_group_lyt)
        self.task_group_label = QtWidgets.QLabel()

        # Path label: Show the title scene path
        path_label = QtWidgets.QLabel("Scene Path: ")
        # Line edit: Line with the path of the scene
        self.path = QtWidgets.QLineEdit()

        # Tool Button: Dialog File scene
        btn_file = QtWidgets.QToolButton()
        btn_file.clicked.connect(self.dialog_scene_directory)
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)
        btn_file.setIcon(icon)

        # Checkbox: Creates a project directory
        self.project_dir = QtWidgets.QCheckBox("Project directory")
        self.project_dir.stateChanged.connect(self.scene_directory)
        # Checkbox: Creates a scenes directory
        self.scene_dir = QtWidgets.QCheckBox("Scene directory")
        self.scene_dir.stateChanged.connect(self.scene_directory)

        # ASSETS PATH
        # Label: Assets path title
        assets_label = QtWidgets.QLabel("Assets Path:")

        # Line edit: Assets path
        self.assets_path = QtWidgets.QLineEdit()

        # Tool Button: Dialog File assets
        btn_file_assets = QtWidgets.QToolButton()
        btn_file_assets.clicked.connect(self.dialog_assets_directory)
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)
        btn_file_assets.setIcon(icon)

        # Checkbox: Creates a project directory
        self.project_dir_assets = QtWidgets.QCheckBox("Project directory")
        self.project_dir_assets.stateChanged.connect(self.assets_directory)
        # Checkbox: Creates a scenes directory
        self.assets_dir = QtWidgets.QCheckBox("Assets directory")
        self.assets_dir.stateChanged.connect(self.assets_directory)

        # ADD ELEMENTS TO THE LAYOUT
        self.grid_lyt.addWidget(disks_group, 3, 0)
        self.grid_lyt.addWidget(project_group, 3, 1)
        self.grid_lyt.addWidget(seq_group, 3, 2)
        self.grid_lyt.addWidget(shot_group, 3, 3)
        self.grid_lyt.addWidget(task_group, 3, 4)
        self.grid_lyt.addWidget(path_label, 4, 0)
        self.grid_lyt.addWidget(self.path, 4, 1)
        self.grid_lyt.addWidget(btn_file, 4, 2, alignment=QtCore.Qt.AlignCenter)
        self.grid_lyt.addWidget(self.project_dir, 4, 3)
        self.grid_lyt.addWidget(self.scene_dir, 4, 4)
        self.grid_lyt.addWidget(assets_label, 5, 0)
        self.grid_lyt.addWidget(self.assets_path, 5, 1)
        self.grid_lyt.addWidget(btn_file_assets, 5, 2,
                                alignment=QtCore.Qt.AlignCenter)
        self.grid_lyt.addWidget(self.project_dir_assets, 5, 3)
        self.grid_lyt.addWidget(self.assets_dir, 5, 4)

    def scene_load_layout(self):
        """ Creates the button load scene."""
        # BUTTON CREATE SCENE
        # Button: Load Scene
        btn = QtWidgets.QPushButton("Scene Build")
        btn.clicked.connect(self.notes)
        btn.clicked.connect(self.download_drive_assets)
        btn.clicked.connect(self.download_assets_dialog)

        # ADD ELEMENTS TO THE LAYOUTS
        self.btn_lyt.addWidget(btn)

    def change_cheks(self):
        """ Method that change the checkboxes to False."""
        self.check_notes.setChecked(False)
        self.assets_check.setChecked(False)
        self.project_dir.setChecked(False)
        self.scene_dir.setChecked(False)
        self.project_dir_assets.setChecked(False)
        self.assets_dir.setChecked(False)

    def exec_functions(self):
        """ Executes all the method and functions that I need."""
        jsonFlow.JsonFlowData().create_json()
        self.table.deleteLater()
        self.text_update.deleteLater()
        self.change_cheks()
        self.path.setText("")
        try:
            self.task_text = ""
            self.notes_text.clear()
        except:
            pass

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

    def build_tasks(self):
        """ Tasks data based on use at the table widget

        :return: List with a list with each task assigned to the user
        :rtype: list
        """
        try:
            # Get the dictionary tasks from json data
            tasks = self.get_json_tasks()["Tasks"]
            # Comprehension dict with sequence data
            sequence_list = {"sequence": [sequence["entity"]["name"].split("_")[0]
                             for sequence in tasks]}

            # Fields to get for the 3 firsts columns
            # Shot | Project | Department build
            fields = ["entity", "project", "step"]
            # Comprehension dict with 3 firsts columns data
            extracted_fields = {field: [f[field]["name"] for f in tasks]
                                for field in fields}

            # Fields to get the following columns
            # Task | Satus | Priority | Start dt | End dt| Description build
            other_fields = ["content", "sg_status_list", "sg_priority_1",
                            "start_date", "due_date", "sg_description"]
            # Comprehension dict with the following columns data
            extracted_other_fields = {field: [t[field] for t in tasks]
                                      for field in other_fields}

            # Combine the dict data of each tasks at a list to create the table
            tasks_list = [
                sequence_list["sequence"],
                extracted_fields["entity"],
                extracted_fields["project"],
                extracted_fields["step"],
                extracted_other_fields["content"],
                extracted_other_fields["sg_status_list"],
                extracted_other_fields["sg_priority_1"],
                extracted_other_fields["start_date"],
                extracted_other_fields["due_date"],
                extracted_other_fields["sg_description"]
            ]

            return tasks_list

        except:
            pass

    def detect_disks(self):
        """ Detect the disks at the pc and return it in a list

        :return: List with all de devices/disks at the pc
        :rtype: list
        """
        # List of all disk partitions on the system
        disks = psutil.disk_partitions()
        disk_list = []
        # Get the disk partitions and append to the list
        for disk in disks:
            dev = disk.device
            dev1 = dev.replace("\\", "/")
            disk_list.append(dev1)

        return disk_list

    def create_scene_path(self):
        """ Create a path using the table data and groups of boxes."""
        self.project_dir.setChecked(False)
        self.scene_dir.setChecked(False)
        self.project_dir_assets.setChecked(False)
        self.assets_dir.setChecked(False)

        try:
            current_row = self.table.currentRow()
            total_columns = self.table.columnCount()

            # Loop through each row and columns to get the selected data
            table_data = [self.table.item(current_row, column).text()
                          for column in range(total_columns)]

            # Get the project and set it
            self.project_group_label.setText(table_data[2])
            self.project_group_lyt.addWidget(self.project_group_label)
            self.project_text = self.project_group_label.text()

            # Get the sequence and set it
            self.seq_group_label.setText(table_data[0])
            self.seq_group_lyt.addWidget(self.seq_group_label)
            self.sequence_text = self.seq_group_label.text()

            # Get the shot and set it
            self.shot_group_label.setText(table_data[1])
            self.shot_group_lyt.addWidget(self.shot_group_label)
            self.shot_text = self.shot_group_label.text()

            # Get the task and set it
            self.task_group_label.setText(table_data[4])
            self.task_group_lyt.addWidget(self.task_group_label)
            self.task_text = self.task_group_label.text()

            # Detect with te signal the current disk at the menu
            self.disk_text = self.menu_disks.currentText()

            # Get the username of the system
            os_user = os.environ["USERNAME"]

            # Creates the path to save the scene
            if self.disk_text == "C:/":
                self.mega_path = f"{self.disk_text}Users/{os_user}/"
                self.assets_path.setText(self.mega_path)

            else:
                self.mega_path = f"{self.disk_text}"
                self.assets_path.setText(self.mega_path)

            self.complete_path = f"{self.mega_path}{self.project_text}_{self.sequence_text}_" \
                                 f"{self.shot_text}_{self.task_text}.hip"

            self.path.setText(self.complete_path)

        except:
            self.path.setText("")

    def warning_message(self):
        """ Warning message if no task is selected in the table."""
        # Create the dialog
        message = QtWidgets.QMessageBox(self)
        # Set window title
        message.setWindowTitle("WARNING!!")
        message.setText("Select a task at the table")
        message.setDetailedText("You must select a task from the table "
                                "in order to be able to create the path")

        self.change_cheks()

        # Icon Severity
        message.setIcon(QtWidgets.QMessageBox.Warning)
        message.exec_()

    def notes(self):
        """ Get and set the notes of each task from the flow
            by the json data.
        """
        try:
            if self.check_notes.isChecked():
                # Get the notes at the json data
                notes_res = self.get_json_tasks()["Notes"]

                for note in notes_res:
                    # Get the tasks in the notes data and set the notes
                    for task in note["tasks"]:
                        if self.task_text == task["name"]:
                            self.content = note["content"]
                            self.notes_text.setText(self.content)
            else:
                # Delete the notes if isn't checked
                self.notes_text.clear()
        except:
            self.warning_message()

    def get_assets(self):
        """ Get assets of each shot from flow and show in a list widget."""
        try:
            if self.assets_check.isChecked():
                self.json_assets = self.get_json_tasks()["Assets"]

                assets_list = [asset["code"] for asset in self.json_assets
                               for shot in asset["shots"]
                               if self.shot_text == shot["name"]]

                self.assets_list.addItems(assets_list)

            else:
                self.assets_list.clear()
                self.import_assets_list.clear()

        except:
            self.warning_message()

    def assets_to_import(self):
        """ Gets the assets selected of the assets list and creates a new
            list for add this in a list that the assets are ready to import.

        :return: List with assets to import
        :rtype: List
        """
        # Gets the selected assets
        txt = self.assets_list.selectedItems()
        # List comprehension that add these assets to an import list
        import_assets = [t.text() for t in txt]

        return import_assets

    def assets_move(self):
        """ Add the assets to the list using a tool button move."""
        self.import_assets_list.addItems(self.assets_to_import())

    def assets_to_remove(self):
        """ Gets the assets selected of the assets import list and creates a new
            list for add this in a list that the assets are ready to be deleted.

        :return: List with assets to delete
        :rtype: List
        """
        # List comprehension that add these assets to a remove list
        remove_assets = [t for t in self.import_assets_list.selectedItems()]

        return remove_assets

    def asset_delete(self):
        """ Delete the assets at the remove_assets using a tool button delete."""
        # Gets each asset individually
        for remove in self.assets_to_remove():
            # Get the asset index with the .row and delete with the takeItem
            self.import_assets_list.takeItem(self.import_assets_list.row(remove))

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # Add the text of the dragged item to the import assets list
        text = event.source().currentItem().text()
        self.import_assets_list.addItem(text)
        event.accept()

    def keyPressEvent(self, event):
        # Detects when key delete is pressed
        if event.key() == QtCore.Qt.Key_Delete:
            for asset in self.assets_to_remove():
                # Get the asset index with the .row and delete with the takeItem
                self.import_assets_list.takeItem(self.import_assets_list.row(asset))

    def web_github(self):
        webbrowser.open("https://github.com/Raul-Olivares-TD")

    def web_linkedin(self):
        webbrowser.open("https://www.linkedin.com/in/raul-olivares-fx/")

    def dialog_scene_directory(self):
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

        self.project_dir.setChecked(False)
        self.scene_dir.setChecked(False)

        # Creates the path with the dialog directory
        try:
            if path == "":
                self.path.setText("")
            elif len(path) == 3:
                rep_path = path.replace("/", "")
                self.path.setText(f"{rep_path}/"
                                  f"{os.path.basename(self.complete_path)}")
            else:
                self.path.setText(f"{path}/"
                                  f"{os.path.basename(self.complete_path)}")

        except:
            self.warning_message()

    def scene_directory(self):
        """ Adds the project directory and the scenes directory to the paths
            if the checks of that options are checked.
        """
        try:
            # Gets the dirname of the path
            dirname = os.path.dirname(self.complete_path)
            # Gets the basename of the path
            basename = os.path.basename(self.complete_path)
            # String with the project name
            project_folder = self.project_text
            # String with the text scenes
            scene_folder = "scenes"

            # Check different options to create or not any directory
            if os.path.splitdrive(self.complete_path)[0] != "C:":
                if self.project_dir.isChecked() and self.scene_dir.isChecked():
                    self.path.setText(f"{dirname}{project_folder}/{scene_folder}/"
                                      f"{basename}")

                elif self.project_dir.isChecked():
                    self.path.setText(f"{dirname}{project_folder}/"
                                      f"{basename}")

                elif self.scene_dir.isChecked():
                    self.path.setText(f"{dirname}{scene_folder}/"
                                      f"{basename}")

                else:
                    self.complete_path = f"{self.mega_path}{self.project_text}_{self.sequence_text}_" \
                                         f"{self.shot_text}_{self.task_text}.hip"
                    self.path.setText(self.complete_path)

            else:
                if self.project_dir.isChecked() and self.scene_dir.isChecked():
                    self.path.setText(f"{dirname}/{project_folder}/{scene_folder}/"
                                      f"{basename}")

                elif self.project_dir.isChecked():
                    self.path.setText(f"{dirname}/{project_folder}/"
                                      f"{basename}")

                elif self.scene_dir.isChecked():
                    self.path.setText(f"{dirname}/{scene_folder}/"
                                      f"{basename}")

                else:
                    self.complete_path = f"{self.mega_path}{self.project_text}_{self.sequence_text}_" \
                                         f"{self.shot_text}_{self.task_text}.hip"
                    self.path.setText(self.complete_path)
        except:
            self.warning_message()

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

        self.assets_dir.setChecked(False)
        self.project_dir_assets.setChecked(False)

        # Creates the path with the dialog directory
        if path == "":
            self.path.setText("")
        elif len(path) == 3:
            rep_path = path.replace("/", "")
            self.assets_path.setText(f"{rep_path}/")

        else:
            self.assets_path.setText(f"{path}/")

    def assets_directory(self):
        """ Adds the project directory and the assets directory to the paths
            if the checks of that options are checked.
        """
        try:
            # Gets the dirname of the path
            dirname = os.path.dirname(self.complete_path)
            # Gets the basename of the path
            basename = os.path.basename(self.complete_path)
            # String with the project name
            p_folder = self.project_text
            # String with the text scenes
            assets_folder = "assets"

            # Check different options to create or not any directory
            if os.path.splitdrive(self.complete_path)[0] != "C:":
                if self.project_dir_assets.isChecked() and self.assets_dir.isChecked():
                    self.assets_path.setText(f"{dirname}{p_folder}/{assets_folder}/")

                elif self.project_dir_assets.isChecked():
                    self.assets_path.setText(f"{dirname}{p_folder}/")

                elif self.assets_dir.isChecked():
                    self.assets_path.setText(f"{dirname}{assets_folder}/")

                else:
                    self.assets_path.setText(f"{self.mega_path}")

            else:
                if self.project_dir_assets.isChecked() and self.assets_dir.isChecked():
                    self.assets_path.setText(f"{dirname}/{p_folder}/{assets_folder}/")

                elif self.project_dir_assets.isChecked():
                    self.assets_path.setText(f"{dirname}/{p_folder}/")

                elif self.assets_dir.isChecked():
                    self.assets_path.setText(f"{dirname}/{assets_folder}/")

                else:
                    self.assets_path.setText(f"{self.mega_path}")

        except:
            self.warning_message()

    def download_drive_assets(self):
        """ Download from Google Drive the assets at the import_assets_list
            to the scene.
        """
        # Dict with assets versions from the json
        versions_dict = jsonFlow.JsonFlowData().assets_versions()
        # Get the items at the import_assets_list
        count = self.import_assets_list.count()
        items = [self.import_assets_list.item(item).text()
                 for item in range(count)]

        # List with the ids from the files
        self.drive_ids = []

        for k, v in versions_dict.items():
            asset = k.split("_")[0]
            if asset in items:
                drive_link = v[0]
                drive_id = drive_link.split("/")[-2]
                self.drive_ids.append(drive_id)

    def download_assets_dialog(self):
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
        # Second threat download call
        self.thread = DownloadThread(self.drive_ids, self.assets_path.text())
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

    def files_download_list(self):
        """ Convert the list of the files in a set because the list
            updates with each chunk and the file repeats.
        :return: A set with all the files downloaded
        :rtype: set
        """
        files_set = set(self.thread.downloaded_files)
        return files_set

    def download_finished(self):
        """ Closes the download dialog, shows a completion message
            and call for imports assets into the scene.
        """
        # Close dialog after finish
        self.download_dlg.close()
        # Show where the files saved
        hou.ui.displayMessage(f"Files download at {self.assets_path.text()}")
        # Call the import assets into scene
        self.import_assets_to_scene()

    def import_assets_to_scene(self):
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
                            f"{self.assets_path.text()}{name}.{ext}")
                            abc_arch.parm("buildHierarchy").pressButton()
                            abc_arch.setPosition((0, -3))

                        # If the assets is an alembic but isn't a camera
                        else:
                            abc_file = geo.createNode("alembic", name)
                            abc_file.parm("fileName").set(
                                f"{self.assets_path.text()}{name}.{ext}")
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
                            fbx_char.parm("fbxfile").set(f"{self.assets_path.text()}"
                                                         f"{name}.{ext}")
                            null = fbx_char.createOutputNode("null",
                                                             f"OUT_{name.upper()}")
                            merge.setNextInput(null)

                        # If the asset haven't skeleton
                        else:
                            fbx_file = geo.createNode("file")
                            fbx_file.parm("file").set(f"{self.assets_path.text()}"
                                                      f"{name}.{ext}")
                            transform = fbx_file.createOutputNode("xform")
                            transform.parm("scale").set(0.01)
                            null = transform.createOutputNode("null",
                                                              f"OUT_{name.upper()}")
                            merge.setNextInput(null)

                    # Assets that isn't abc or fbx and need a file node to import
                    else:
                        file = geo.createNode("file")
                        file.parm("file").set(f"{self.assets_path.text()}"
                                              f"{name}.{ext}")
                        transform = file.createOutputNode("xform")
                        transform.parm("scale").set(0.01)
                        null = transform.createOutputNode("null",
                                                          f"OUT_{name.upper()}")
                        merge.setNextInput(null)

        # Sort the nodes
        obj.layoutChildren()
        geo.layoutChildren()
        self.build_scene()

    def build_scene(self):
        """Creates a Houdini scene with structured sticky notes and saves the project.
        - Adds a sticky note at the origin with notes content.
        - Adds a sticky note displaying project details (project, sequence, shot, task).
        - Saves the .hip file at the specified path; creates directories if necessary.
        - Closes the current UI after the operation.
        """
        # Creates an obj path
        obj = hou.node("/obj")

        # Creates the project details note
        try:
            note = obj.createStickyNote()
            note.setText(self.content)
            note.setPosition((0, 0))

        except:
            note.destroy()

        # Creates the notes content
        notes_content = obj.createStickyNote()
        notes_content.setText(f"{self.project_text} -> {self.sequence_text} -> "
                              f"{self.shot_text} -> {self.task_text}")
        notes_content.setPosition((0, 3))
        notes_content.setSize((4, 1))

        # Path for sav
        save_file = self.path.text()
        # Save if the dir exists
        try:
            hou.hipFile.save(save_file)
        # If the dir doesn't exist create it and save
        except:
            save_dir = os.path.dirname(save_file)
            os.makedirs(save_dir)
            hou.hipFile.save(save_file)

        # Close the UI to finish the process
        self.close()


w = SceneBuilder()
w.show()

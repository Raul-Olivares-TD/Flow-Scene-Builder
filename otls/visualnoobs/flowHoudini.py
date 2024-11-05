import json
import jsonFlow
import os
from PySide2 import QtWidgets, QtCore, QtGui
import psutil


class SceneBuilder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.build_layout()
        self.create_table()
        self.build_tasks()

    def build_layout(self):
        """ Creates the UI interfice and his elements."""
        # CREATES LAYOUTS
        main_lyt = QtWidgets.QVBoxLayout()  # Main layout
        hor_lyt = QtWidgets.QHBoxLayout()  # Horizontal layout
        self.table_lyt = QtWidgets.QVBoxLayout()  # Table layout
        btn_lyt = QtWidgets.QHBoxLayout()  # Btn layout
        self.grid_lyt = QtWidgets.QGridLayout()  # Grid layout
        self.assets_btn = QtWidgets.QVBoxLayout() # Asset butons layout

        # SET LAYOUTS
        self.setLayout(main_lyt)
        main_lyt.addLayout(hor_lyt)
        main_lyt.addLayout(self.table_lyt)
        main_lyt.addLayout(self.grid_lyt)
        main_lyt.addLayout(btn_lyt)

        # ELEMENTS
        # Label: Show the User title
        user_label = QtWidgets.QLabel("User: ")

        # Label: Show the Flow user email
        user = QtWidgets.QLabel()
        user.setText("aperonmxr@gmail.com")

        # Button: Update tasks, exec functions and creates the table
        update_btn = QtWidgets.QPushButton("Update Data Flow")
        update_btn.clicked.connect(self.exec_functions)
        update_btn.clicked.connect(self.get_json_tasks)
        update_btn.clicked.connect(self.create_table)

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

        # Tool Button: Dialog File
        btn_file = QtWidgets.QToolButton()
        btn_file.clicked.connect(self.dialog_directory)
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)
        btn_file.setIcon(icon)

        # Checkbox: Creates a project directory
        self.project_dir = QtWidgets.QCheckBox("Project directory")
        self.project_dir.stateChanged.connect(self.add_directory)
        # Checkbox: Creates a scenes directory
        self.scene_dir = QtWidgets.QCheckBox("Scene directory")
        self.scene_dir.stateChanged.connect(self.add_directory)

        # Checkbox: Allows to show the notes
        self.check_notes = QtWidgets.QCheckBox("View Notes")
        self.check_notes.stateChanged.connect(self.notes)
        # Text: Show the notes in a text
        self.notes_text = QtWidgets.QTextEdit()
        self.notes_text.setReadOnly(True)


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
        self.txt_assets_to_import = QtWidgets.QLabel("Assets to import")

        # List: Assets list that will be imported in the scene
        self.import_assets_list = QtWidgets.QListWidget()
        self.import_assets_list.setAcceptDrops(True)
        self.import_assets_list.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.import_assets_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.import_assets_list.itemSelectionChanged.connect(self.assets_to_remove)

        # Button: Load Scene
        btn = QtWidgets.QPushButton("Scene Build")
        btn.clicked.connect(self.notes)
        btn.clicked.connect(self.build_scene)

        # ADD ELEMENTS TO THE LAYOUTS
        # Adds to the Horizontal layout
        hor_lyt.addWidget(user_label)
        hor_lyt.addWidget(user)
        hor_lyt.addWidget(update_btn)
        self.assets_btn.addWidget(self.btn_move)
        self.assets_btn.addWidget(self.btn_delete)

        # Adds to the Grid Layout
        self.grid_lyt.addWidget(disks_group, 1, 0)
        self.grid_lyt.addWidget(project_group, 1, 1)
        self.grid_lyt.addWidget(seq_group, 1, 2)
        self.grid_lyt.addWidget(shot_group, 1, 3)
        self.grid_lyt.addWidget(task_group, 1, 4)
        self.grid_lyt.addWidget(path_label, 2, 0)
        self.grid_lyt.addWidget(self.path, 2, 1)
        self.grid_lyt.addWidget(btn_file, 2, 2, alignment=QtCore.Qt.AlignCenter)
        self.grid_lyt.addWidget(self.project_dir, 2, 3)
        self.grid_lyt.addWidget(self.scene_dir, 2, 4)
        self.grid_lyt.addWidget(self.check_notes, 3, 0)
        self.grid_lyt.addWidget(self.assets_check, 3, 1)
        self.grid_lyt.addWidget(self.txt_assets_to_import, 3, 3)
        self.grid_lyt.addWidget(self.notes_text, 4, 0)
        self.grid_lyt.addWidget(self.assets_list, 4, 1)
        self.grid_lyt.addLayout(self.assets_btn, 4, 2,
                                alignment=QtCore.Qt.AlignCenter)
        self.grid_lyt.addWidget(self.import_assets_list, 4, 3)

        # Adds the Button Horizontal layout
        btn_lyt.addWidget(btn)

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
            self.table_lyt.addWidget(self.table)

        except:
            # Text Update Data Flow
            self.text_update = QtWidgets.QTextEdit()
            self.text_update.setText("UPDATE THE DATA FLOW")
            self.text_update.setAlignment(QtCore.Qt.AlignCenter)
            # Modify the font size
            font = self.text_update.font()
            font.setPointSize(42)
            self.text_update.setFont(font)
            self.table_lyt.addWidget(self.text_update)

    def change_cheks(self):
        """ Method that change the checkboxes to False."""
        self.project_dir.setChecked(False)
        self.scene_dir.setChecked(False)
        self.check_notes.setChecked(False)
        self.assets_check.setChecked(False)

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
        self.change_cheks()

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

            else:
                self.mega_path = f"{self.disk_text}"

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

    def dialog_directory(self):
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

        self.change_cheks()

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

    def add_directory(self):
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
                            content = note["content"]
                            self.notes_text.setText(content)
            else:
                # Delete the notes if isn't checked
                self.notes_text.clear()
        except:
            self.warning_message()

    def get_assets(self):
        """ Get assets of each shot from flow and show in a list widget."""
        try:
            if self.assets_check.isChecked():
                json_assets = self.get_json_tasks()["Assets"]

                assets_list = [asset["code"] for asset in json_assets
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
        for t in self.assets_to_remove():
            # Get the asset index with the .row and delete with the takeItem
            self.import_assets_list.takeItem(self.import_assets_list.row(t))

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        # Add the text of the dragged item to the import assets list
        text = event.source().currentItem().text()
        self.import_assets_list.addItem(text)
        event.accept()

    def build_scene(self):
        #
        # obj = hou.node("/obj")
        #
        # try:
        #     note = obj.createStickyNote()
        #     note.setText(self.content)
        #     note.setPosition((0, 0))
        #
        # except:
        #     note.destroy()
        #
        # w_data = obj.createStickyNote()
        # w_data.setText(f"{self.project_text} -> {self.sequence_text} -> "
        #                f"{self.shot_text} -> {self.task_text}")
        # w_data.setPosition((0, 4))
        # w_data.setSize((4, 1))
        #
        # save_file = self.path.text()
        # try:
        #     hou.hipFile.save(save_file)
        # except:
        #     save_dir = os.path.dirname(save_file)
        #     os.makedirs(save_dir)
        #     hou.hipFile.save(save_file)

        self.close()


app = QtWidgets.QApplication([])
w = SceneBuilder()
w.show()
app.exec_()

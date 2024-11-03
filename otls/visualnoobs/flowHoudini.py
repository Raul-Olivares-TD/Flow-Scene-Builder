import json
import jsonFlow
import os
from PySide2 import QtWidgets
import psutil


class SceneBuilder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.build_layout()
        self.create_table()
        self.build_tasks()

    def build_layout(self):
        """ Creates the UI interfice and his elements."""
        # CREATES LAYOUT
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
        # Label Widget
        user_label = QtWidgets.QLabel("User: ")

        # Flow User
        user = QtWidgets.QLabel()
        user.setText("aperonmxr@gmail.com")

        # Update tasks
        update_btn = QtWidgets.QPushButton("Update Data Flow")
        update_btn.clicked.connect(self.exec_functions)
        update_btn.clicked.connect(self.get_json_tasks)
        update_btn.clicked.connect(self.create_table)

        # Disks Group
        disks_group = QtWidgets.QGroupBox("Device")
        disks_group_lyt = QtWidgets.QVBoxLayout()
        disks_group.setLayout(disks_group_lyt)

        # Menu disks
        self.menu_disks = QtWidgets.QComboBox()
        # self.menu_disks.addItem("")
        self.menu_disks.addItems(self.detect_disks())
        disks_group_lyt.addWidget(self.menu_disks)
        self.menu_disks.currentTextChanged.connect(self.create_scene_path)

        # Project Group
        project_group = QtWidgets.QGroupBox("Project")
        self.project_group_lyt = QtWidgets.QVBoxLayout()
        project_group.setLayout(self.project_group_lyt)
        self.project_group_label = QtWidgets.QLabel()

        # Sequence Group
        seq_group = QtWidgets.QGroupBox("Sequence")
        self.seq_group_lyt = QtWidgets.QVBoxLayout()
        seq_group.setLayout(self.seq_group_lyt)
        self.seq_group_label = QtWidgets.QLabel()

        # Shot Group
        shot_group = QtWidgets.QGroupBox("Shot")
        self.shot_group_lyt = QtWidgets.QVBoxLayout()
        shot_group.setLayout(self.shot_group_lyt)
        self.shot_group_label = QtWidgets.QLabel()

        # Task group
        task_group = QtWidgets.QGroupBox("Task")
        self.task_group_lyt = QtWidgets.QVBoxLayout()
        task_group.setLayout(self.task_group_lyt)
        self.task_group_label = QtWidgets.QLabel()

        # Path label
        path_label = QtWidgets.QLabel("Scene Path: ")
        # Path
        self.path = QtWidgets.QLineEdit()

        # Tool Button dialog File
        btn_file = QtWidgets.QToolButton()
        btn_file.clicked.connect(self.dialog_directory)
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_DirIcon)
        btn_file.setIcon(icon)

        # Checkbox Project Directory
        self.project_dir = QtWidgets.QCheckBox("Project directory")
        self.project_dir.stateChanged.connect(self.add_directory)
        # Checkbox Scene Directory
        self.scene_dir = QtWidgets.QCheckBox("Scene directory")
        self.scene_dir.stateChanged.connect(self.add_directory)
        # Checkbox Notes
        self.check_notes = QtWidgets.QCheckBox("View Notes:")
        self.check_notes.stateChanged.connect(self.notes)

        # Assets
        self.assets_check = QtWidgets.QCheckBox("Get Assets")
        self.assets_check.stateChanged.connect(self.get_assets)
        self.assets_check.stateChanged.connect(self.assets_move)

        # Asset Butons for pass the assets to the import list
        self.btn_pase = QtWidgets.QToolButton()
        self.btn_pase.clicked.connect(self.assets_move)
        self.btn_delete = QtWidgets.QToolButton()

        # Label Assets to import
        self.txt_assets_to_import = QtWidgets.QLabel("Assets to import")

        # Button load Scene
        btn = QtWidgets.QPushButton("Scene Build")
        btn.clicked.connect(self.notes)
        btn.clicked.connect(self.build_scene)

        # ADD ELEMENTS TO THE LAYOUTS
        # Adds to the Horizontal layout
        hor_lyt.addWidget(user_label)
        hor_lyt.addWidget(user)
        hor_lyt.addWidget(update_btn)
        self.assets_btn.addWidget(self.btn_pase)
        self.assets_btn.addWidget(self.btn_delete)

        # Adds to the Grid Layout
        self.grid_lyt.addWidget(disks_group, 1, 0)
        self.grid_lyt.addWidget(project_group, 1, 1)
        self.grid_lyt.addWidget(seq_group, 1, 2)
        self.grid_lyt.addWidget(shot_group, 1, 3)
        self.grid_lyt.addWidget(task_group, 1, 4)
        self.grid_lyt.addWidget(path_label, 2, 0)
        self.grid_lyt.addWidget(self.path, 2, 1)
        self.grid_lyt.addWidget(btn_file, 2, 2)
        self.grid_lyt.addWidget(self.project_dir, 2, 3)
        self.grid_lyt.addWidget(self.scene_dir, 2, 4)
        self.grid_lyt.addWidget(self.check_notes, 3, 0)
        self.grid_lyt.addWidget(self.assets_check, 3, 1)
        self.grid_lyt.addWidget(self.txt_assets_to_import, 3, 3)
        self.grid_lyt.addLayout(self.assets_btn, 4, 2)

        # Adds to the Button Horizontal layout
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
            # Probar a hacer un text edit con el texto update cuando no hay tabla
            # y que se elimine en el create_json_data con el deleteLater
            pass

    def change_cheks(self):
        self.project_dir.setChecked(False)
        self.scene_dir.setChecked(False)
        self.check_notes.setChecked(False)
        self.assets_check.setChecked(False)

    def exec_functions(self):
        """ Executes all the method and functions that I need."""
        jsonFlow.JsonFlowData().create_json()
        self.table.deleteLater()
        self.change_cheks()
        self.path.setText("")
        try:
            self.task_text = ""
            self.notes_text.deleteLater()
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
        disks = psutil.disk_partitions()
        disk_list = []
        for disk in disks:
            dev = disk.device
            dev1 = dev.replace("\\", "/")
            disk_list.append(dev1)

        return disk_list

    def create_scene_path(self):
        self.change_cheks()

        try:
            current_row = self.table.currentRow()
            total_columns = self.table.columnCount()

            table_data = [self.table.item(current_row, column).text()
                          for column in range(total_columns)]

            self.project_group_label.setText(table_data[2])
            self.project_group_lyt.addWidget(self.project_group_label)
            self.project_text = self.project_group_label.text()

            self.seq_group_label.setText(table_data[0])
            self.seq_group_lyt.addWidget(self.seq_group_label)
            self.sequence_text = self.seq_group_label.text()

            self.shot_group_label.setText(table_data[1])
            self.shot_group_lyt.addWidget(self.shot_group_label)
            self.shot_text = self.shot_group_label.text()

            self.task_group_label.setText(table_data[4])
            self.task_group_lyt.addWidget(self.task_group_label)
            self.task_text = self.task_group_label.text()

            self.disk_text = self.menu_disks.currentText()

            os_user = os.environ["USERNAME"]

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
        # Crear el dialog
        message = QtWidgets.QMessageBox(self)
        # Poner el titulo de la ventana
        message.setWindowTitle("WARNING!!")
        message.setText("Select a task at the table")
        message.setDetailedText("You must select a task from the table "
                                "in order to be able to create the path")

        self.change_cheks()

        # Icono Severity q en la documentacón te dicen cuales hay
        message.setIcon(QtWidgets.QMessageBox.Warning)
        message.exec_()

    def dialog_directory(self):
        # Crear el dialog
        path = QtWidgets.QFileDialog.getExistingDirectory(
            # parent a la misma ventana
            self,
            # Titulo de la ventana
            "Select Custom Path",
            # En q disco buscar por defecto
            "C:"

        )

        self.change_cheks()

        try:
            if path == "":
                # Esto devuevle el path en forma de tuple seleccionado en la carpeta
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
        """ Testing for now.
        """
        try:
            dirname = os.path.dirname(self.complete_path)
            basename = os.path.basename(self.complete_path)
            project_folder = self.project_text
            scene_folder = "scenes"

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
        """ Testing for now.
        """
        try:
            if self.check_notes.isChecked():
                r = self.get_json_tasks()["Notes"]
                # Notes text
                self.notes_text = QtWidgets.QTextEdit()
                self.notes_text.setReadOnly(True)
                self.grid_lyt.addWidget(self.notes_text, 4, 0)

                for i in r:
                    for j in i["tasks"]:
                        if self.task_text == j["name"]:
                            content = i["content"]
                            self.notes_text.setText(content)
            else:
                self.notes_text.deleteLater()
        except:
            self.warning_message()

    def get_assets(self):
        """ Testing for now.
        """
        try:
            if self.assets_check.isChecked():
                json_assets = self.get_json_tasks()["Assets"]
                # Assets list
                self.assets_list = QtWidgets.QListWidget()
                self.import_assets_list = QtWidgets.QListWidget()
                self.assets_list.setSelectionMode(
                    QtWidgets.QAbstractItemView.ExtendedSelection)
                assets_list = []

                assets_list += [asset["code"] for asset in json_assets
                               for shot in asset["shots"]
                               if self.shot_text == shot["name"]]

                self.assets_list.addItems(assets_list)
                self.grid_lyt.addWidget(self.assets_list, 4, 1)
                self.grid_lyt.addWidget(self.import_assets_list, 4, 3)
                self.assets_list.itemSelectionChanged.connect(self.assets_to_import)
            else:
                self.assets_list.deleteLater()
                self.import_assets_list.deleteLater()
                
        except:
            self.warning_message()

    def assets_to_import(self):
        txt = self.assets_list.selectedItems()
        import_list = [t.text() for t in txt]

        return import_list

    def assets_move(self):
        # self.import_assets_list.addItems(self.assets_to_import())
        pass




    def asset_delete(self):
        pass

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

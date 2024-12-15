import hou
import json
import os
import shotgun_api3

class JsonFlowData():
    def __init__(self):
        """Authentication for access to flow data."""
        self.sg = shotgun_api3.Shotgun(
            "https://dramastudio.shotgrid.autodesk.com/",
            script_name="tdscript",
            api_key="rkmbtqY#7tjjxtxplsbvodaaq")

        self.data_flow()
        self.create_path()

    def data_flow(self):
        """ Gets data on the projects in which the artist participates.

        :return: A dict with the user projects data
        :rtype: dict
        """
        # FLOW user for search the data
        SG_USER = os.environ["FLOW_USER"]

        # Serch if the user is in the project
        filters = [
            ["email", "is", SG_USER]
        ]

        # Response find to flow for get data
        self.user_data = self.sg.find("HumanUser", filters=filters, fields=["projects"])[0]
        # Gets the info of the project
        user_projects = self.user_data["projects"]

        return user_projects

    def data_tasks(self):
        """ Gets the task data.

        :return: A list with a dict with the task data assign to the user
        :rtype: list
        """        
        tasks_list = []
        for user_project in self.data_flow():
            filters = [
                ["project", "is", {"type": "Project", "id": user_project["id"]}],
                ["task_assignees", "is", self.user_data]
            ]

            fields = ["content", "project",
                      "task_assignees", "entity", "step",
                      "sg_status_list", "start_date",
                      "due_date", "sg_priority_1",
                      "sg_description", ]

            user_tasks = self.sg.find("Task", filters, fields=fields)

            tasks_list += [u for u in user_tasks]

        return tasks_list

    def data_notes(self):
        """ Gets the notes of each task.

        :return: A list with a dict with the task notes
        :rtype: list
        """  
        note_list = []
        for user_project in self.data_flow():
            filters = [
                ["project", "is", {"type": "Project", "id": user_project["id"]}]
            ]

            notes = self.sg.find("Note",filters,["content", "tasks",
                                                 "note_links"])

            note_list += [note for note in notes]


        return note_list

    def data_assets(self):
        """ Gets the assets data.

        :return: A list with the filters of the assets that we need
        :rtype: list
        """
        assets_list = []
        for user_project in self.data_flow():
            filters = [
                ["project", "is", {"type": "Project", "id": user_project["id"]}],
            ]

            assets = self.sg.find("Asset", filters, ["code", "sg_asset_type",
                                                     "sg_versions", "shots",
                                                     "sg_status_list"])

            assets_list += [asset for asset in assets]


        return assets_list

    def assets_versions(self):
        """ Gets the versions of each asset at the project.

        :return: A dict with the assets versions that we need
        :rtype: dict
        """
        drive_assets = {}
        for user_project in self.data_flow():
            # Required filters
            filters = [
                ["project", "is", {"type": "Project", "id": user_project["id"]}],
            ]

            # Requiered fields 
            fields = ["code", "sg_status_list", "sg_path_to_geometry"]

            # Response find to flow for get data
            versions = self.sg.find("Version", filters, fields)

            # Gets the version that is approved
            for version in versions:
                ver = version["code"]
                link = version["sg_path_to_geometry"]
                if version["sg_status_list"] == "apr":
                    if ver in drive_assets:
                        drive_assets[ver].append(link)
                    else:
                        drive_assets[ver] = [link]

        return drive_assets

    def create_path(self):
        """ Create the path for save the json using the current version of the
            houdini used."""  
        # Gets the username of the pc
        username = os.environ["USERNAME"]
        # Gets the current houdini version
        houdini_version = hou.applicationVersionString()
        # Building the path
        v_split = houdini_version.split(".")
        hou_v = "houdini"+".".join([v_split[0], v_split[1]])
        # Path to save the json
        self.path = f"C:/Users/{username}/Documents/{hou_v}/otls/flowJson"
        # Path and file name
        self.file = f"{self.path}/dataFlow.json"

    def create_json(self):
        """ Creates the json."""
        d = {}
        d["Tasks"] = self.data_tasks()
        d["Notes"] = self.data_notes()
        d["Assets"] = self.data_assets()

        try:
            os.makedirs(self.path)
            with open(self.file, "w") as f:
                json.dump(d, f, indent=4)
        except:
            with open(self.file, "w") as f:
                json.dump(d, f, indent=4)

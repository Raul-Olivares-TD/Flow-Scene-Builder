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
        SG_USER = "raul22_1996@outlook.es"

        filters = [
            ["email", "is", SG_USER]
        ]

        self.user_data = self.sg.find("HumanUser", filters=filters, fields=["projects"])[0]
        user_projects = self.user_data["projects"]

        return user_projects

    def data_tasks(self):
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
        note_list = []
        for user_project in self.data_flow():
            filters = [
                ["project", "is", {"type": "Project", "id": user_project["id"]}]
            ]

            notes = self.sg.find("Note",filters,["content", "tasks",
                                                 "note_links"])

            note_list += [note for note in notes]

            # note_list += [note for note in notes for link in note["note_links"]
            #               if link["name"] in self.data_shots()]

        return note_list

    def data_assets(self):
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

    def create_path(self):
        username = os.environ["USERNAME"]
        houdini_version = hou.applicationVersionString()
        v_split = houdini_version.split(".")
        hou_v = "houdini"+".".join([v_split[0], v_split[1]])
        self.path = f"C:/Users/{username}/Documents/{hou_v}/otls/flowJson"
        self.file = f"{self.path}/dataFlow.json"

        return self.file

    def create_json(self):
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

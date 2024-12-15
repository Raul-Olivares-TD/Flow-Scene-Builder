# FLOW SCENE BUILDER

- This is a scene builder tool that merge houdini with Flow/Shotgun/Shotgrid.
- With it the user not need enter to Flow to get the initial steps to work in his tasks.
- This tool gives the user each task they have to work on, with all the necessary data of the project, sequence, shot and task they have to do, it also includes data such as the notes they have left on each task and the necessary assets.
- All of this will be automatically created in a new scene ready to start working
- This tool includes an extra Flow to Houdini importer in case you have left any asset unimported in the scene and we need to work with it.

## HOW TO INSTALL

##### DIRECTORY MANAGEMENT

- Put the directory visualnoobs inside the directory otls at the path at the directory *$HFS* it is the documents directory, something like this: *"C:/Users/User/Documents/houdini20.5/"*.
- The result should be something like: *"C:/Users/User/Documents/houdini20.5/otls/visualnoobs"*.
	- This directory contains inside him 4 scripts to use the tool correctly:
		- **driveDownload.py** -> This scripts have the logic to download assets from Google Drive.
		- **jsonFlow.py** ->  This scripts have the logic to create a json with the flow data.
		- **flowHoudini.py** -> This scripts creates the UI and the scene builder (Main tool).
		- **flowImporter.py** -> This scripts creates a simple UI with an importer from Flow to Houdini, that is a support option if at the scene builder forgot to import some asset that needs at the scene for work.

##### MAIN MENU

- This tool is used at the main menu.
- For this to work properly and be visible in the Houdini main menu put the MainMenuCommon.xml at the path of the *$HFS* *"C:\Users\User\Documents\houdini20.5"*.
- Don't delete any MainMenuCommon.xml of the main path of sidefx Houdini,  this script only add the tool option with out modify the rest of the main menu.

##### HOUDINI.ENV

- Houdini have a houdini.env file in that we need to add this lines.
- Python Path -> For use the scpripts properly at Houdini.
		PYTHONPATH = "C:\Users\User\Documents\houdini20.5\otls\visualnoobs;C:\Users\User\Python\Python311\Lib\site-packages;C:\Users\User\Documents\houdini20.5\otls"
- Flow user -> In that line we must write the user that we have in Flow/ShotGrid/ShotGun.
		FLOW_USER = "email register at flow of each user" # Ex: "jj2inline@gmail.com"
- In the repository the houdini.env file has these lines added, it is only necessary to change the path and the user of the flow correctly.

## HOW TO USE

#### SCENE BUILDER (MAIN TOOL)

##### USE INSTRUCTIONS

- For use the main tool we need to have acces to the Flow API, for this needs the Authentication, somthing like this:
	- shotgun_api3.Shotgun("https://studioname.shotgrid.autodesk.com/", script_name="apiScript",
api_key="ruqwhbkhsadahjsiyuqn")

-  Add the Authentication at the flowJson.py at the init method.
![AuthenticationFLOW](https://github.com/user-attachments/assets/0fc04c66-bc41-4cf3-85b6-4dcbbb647fb6)
- Add the Flow user name of each artist at the houdini.env file.
![FLOW_USER](https://github.com/user-attachments/assets/904ebfa9-cc1e-4134-864f-b8230689c64c)
- The main tool also needs a Google Drive API authentication since we will download the assets from Google Drive.
	- For do that we need to have acces to the Google Drive API like admin or by invited.

##### CREATE GOOGLE DRIVE API

###### 1. Enable the Google Drive API

1. Go to the [Google Drive API Quickstart](https://developers.google.com/drive/api/quickstart/python).
2. Click **Enable the API**.
3. Create a new project if you don’t already have one:
   - Click on your project name at the top left.
   - Select "New Project" and give it a name.
4. Once the project is created, enable the Google Drive API for it.

###### 2. Configure OAuth Consent Screen
1. Go to the [OAuth Consent Screen settings](https://console.cloud.google.com/apis/credentials/consent).
2. Select **External** for app type.
3. Fill in basic app information:
   - App name, email, and other details.
4. Add test users:
   - Include the emails of the users who will test the app.

###### 3. Create API Credentials
1. Go to the [Credentials page](https://console.cloud.google.com/apis/credentials).
2. Click **Create Credentials** → **OAuth Client ID**.
3. Choose "Desktop App" as the application type.
4. Enter a name for the client (e.g., "My Desktop App").
5. Download the credentials JSON file:
   - Save it as `credentials.json` in the folder where your script will run.

###### 4. Use the Credentials in Your Script
- Use the `credentials.json` file to authenticate and access the Google Drive API in your Python script. The [Quickstart guide](https://developers.google.com/drive/api/quickstart/python) provides example code for this step.

##### USE FUNCTION

- UI with a user info at start with a button that allow update the Flow data.
![UISceneBuilder1](https://github.com/user-attachments/assets/24b5ff33-4741-4394-b6c8-1b4a678e855d)

- The next step is show the data at the table with all the tasks of the user have to work.
![UISceneBuilder2](https://github.com/user-attachments/assets/e1f76a3c-b3f7-43b0-9945-1c9b725da160)
	- If you don't have a json at the local path yet, the table is generated empty, press the upload button to download the data.
	![UISceneBuilder3](https://github.com/user-attachments/assets/eec92c91-be6a-44d5-8016-060a80046364)

- By selecting any task from the table we can check the boxes to get the notes of the task, the assets that the shot have and decide what of this assets needs to import to the scene.
![UISceneBuilder4](https://github.com/user-attachments/assets/4fdcc9f2-3a12-440c-af5b-17fc92cbbc09)
	- You can use the buttons to move the assets to the import list or you can also drag and drop and delete them with the delete key on the keyboard.

- When all are ready to create the scene we need to configure the path for save the scene and download the assets from the Google Drive.
![UISceneBuilder5](https://github.com/user-attachments/assets/d134599f-6f34-4ead-98d8-6350f7a1ce78)

- Finally press the Scene Build button and the tool creates a scene at Houdini with all to need for work, assets, stick notes with data and save scene at the pc.

#### FLOW IMPORTER (SUPPORT TOOL)

##### USE INSTRUCTIONS

- For this tool we need again the Authentication from Flow since the code has a different structure than the first tool.
	- Add the Authentication at the FlowConnection class at the init method.
	![FlowImporter1](https://github.com/user-attachments/assets/a0103cea-cd8b-4005-b9ed-24b2edc6a161)
- For the rest of the use it is not necessary to make any new configuration.

##### USE FUNCTION

- User interface with scene data, this data is used to get the assets of this shot and know what we are working on.
![FlowImporter2](https://github.com/user-attachments/assets/e7533c6f-a648-4297-aa18-46e238257cef)

- List of assets that have the shot and need to be checked for import into the scene.
![FlowImporter3](https://github.com/user-attachments/assets/c26d3102-8af3-412a-af39-c36e7ce7d419)

- Path to save the assets, by default is use the same path from the main tool.
![FlowImporter4](https://github.com/user-attachments/assets/881ef314-81ed-46e6-89c5-3e65a0b76756)

- Finally press the Import button for import the assets to the scene.
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

##### FLOW HOUDINI

- For use the main tool we need to have acces to the Flow API, for this needs the Authentication, somthing like this:
	- shotgun_api3.Shotgun("https://studioname.shotgrid.autodesk.com/", script_name="apiScript",
api_key="ruqwhbkhsadahjsiyuqn")

-  Add the Authentication at the flowJson.py at the init method.
![AuthenticationFLOW](https://github.com/user-attachments/assets/0fc04c66-bc41-4cf3-85b6-4dcbbb647fb6)
- Add the Flow user name of each artist at the houdini.env file.
![FLOW_USER](https://github.com/user-attachments/assets/904ebfa9-cc1e-4134-864f-b8230689c64c)
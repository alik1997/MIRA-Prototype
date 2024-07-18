This is prototype developed for demonstrating our idea in Microsoft Ideathon, 2020. MIRA (Medical Identification, Research and Analysis) is a Blockchain based Medical Database System which will store patient's medical records in a secure way and help Government and Concerned authority to predict and analyse different diseases and take necessary steps.

Installation
Install Python 3 in your system. Make sure that pip is available for installing Python packages.
Install virtualenv for creating Python Virtual Environments.
pip install virtualenv
Clone this repository or Extract it into a specific folder and cd into it.
cd MIRA-prototype
Create virtual environment called env using virtualenv.
Linux or Mac
virtualenv -p python3 env
source env/bin/activate
Windows
virtualenv env
env\Scripts\activate
You can use the deactivate command for deactivating the virtual environment.
Install the required Python packages by the command:
pip install -r requirements.txt
Usage
This prototype uses MongoDB as it's database. If MongoDB is not installed in your system, please get it from here

You have to edit and provide own config values in the config.py file.

You can start the Flask app server by calling

python3 main.py
The application can be accessed through a browser at 0.0.0.0:5000

Issues
If you find any bugs/issues or want to request for new feature, please raise an issue.# MIRA-Prototype

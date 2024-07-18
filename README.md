# MIRA Prototype
This is prototype developed for demonstrating our idea in [Microsoft Ideathon, 2020](https://msideathon.in). MIRA (Medical Identification, Research and Analysis) is a Blockchain based Medical Database System which will store patient's medical records in a secure way and help Government and Concerned authority to predict and  analyse different diseases and take necessary steps.

## Installation
1. Install [Python 3](https://www.python.org/) in your system. Make sure that `pip` is available for installing Python packages.
2. Install [`virtualenv`](https://virtualenv.pypa.io/en/latest/) for creating Python Virtual Environments.
    ```bash
    pip install virtualenv
    ```
3. Clone this repository or Extract it into a specific folder and `cd` into it.
    ```bash
    cd MIRA-prototype
    ```
4. Create virtual environment called `env` using `virtualenv`.
    - Linux  or Mac
        ```bash
        virtualenv -p python3 env
        source env/bin/activate
        ```
    - Windows
        ```
        virtualenv env
        env\Scripts\activate
        ```
    You can use the `deactivate` command for deactivating the virtual environment.
5. Install the required Python packages by the command:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. This prototype uses [MongoDB](https://www.mongodb.com) as it's database. If MongoDB is not installed in your system, please get it from [here](https://docs.mongodb.com/guides/server/install/)
   
2. You have to **edit and provide own config values** in the [config.py](config.py) file.

3. You can start the Flask app server by calling
   ```bash
   python3 main.py
   ```
4. The application can be accessed through a browser at [0.0.0.0:5000](http://0.0.0.0:5000/)

## Issues 
If you find any bugs/issues or want to request for new feature, please raise an issue.

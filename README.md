<p align="center">
    <a href="https://docs.icure.com">
        <img alt="icure-your-data-platform-for-medtech-and-ehr" src="https://icure.com/assets/icons/logo.svg">
    </a>
    <h1 align="center">iCure Python Back-End Template</h1>
</p>

Start working on your e-health Python Back-End app with iCure in a few minutes, by using our dedicated template:
```bash
git clone git@github.com:icure/icure-sdk-python-boilerplate-app-template.git my-icure-python-app
```


Once your app is created, complete the file `config.ini` with the following values:
- **parent_organization_username**: The username of your parent organisation to manage medical data through your organisation,
- **parent_organization_token**: The application token (pwd) of your parent organisation to manage medical data through your organisation,
- **parent_organization_public_key** (Optional): The public key of your parent organisation. Complete it only if you already generated cryptographic keys for your parent organisation,
- **parent_organization_private_key** (Optional): The private key of your parent organisation. Complete it only if you already generated cryptographic keys for your parent organisation,
- **host** (Optional): The host to use to start your Node.JS server (127.0.0.1 by default),
- **port** (Optional): The port to use to start your Node.JS server (3000 by default),
- **local_storage_location** (Optional): The path to your local storage file (./scratch/localStorage by default)

Create a Python virtual environment (optional but recommended):
```bash
python3 -m venv icure-sdk
source icure-sdk/bin/activate
```

Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

And start your Python server by executing
```
python3 src/server.py
```

*Confused about the information mentioned above ? Check our [Quick Start](https://docs.icure.com/sdks/quick-start/) to know more about them and how to retrieve them from our [Cockpit Portal](https://cockpit.icure.cloud/)*

Looking for React Native template instead ? Head [here](https://github.com/icure/icure-medical-device-react-native-boilerplate-app-template).

Looking for React.JS template instead ? Head [here](https://github.com/icure/icure-medical-device-react-js-boilerplate-app-template).


## Requirements
Make sure the following tools are installed on your machine:
- [Python 3](https://www.python.org/)


## Which technologies are used ?
- [Python 3](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) for the web server


We chose this set of technologies, because we consider them as the most efficient ones to work with.
Nonetheless, you can of course work with the technologies of your choices and still integrate the iCure SDK in your Python server.


## What includes this template ?
- The [iCure SDK](https://pypi.org/project/icure-sdk/) dependency;
- The cryptographic keys creation of your parent organisation. The first time you'll start your Python server (and go to `http://127.0.0.1:3000`), the template will check if you already provided any cryptographic keys for your parent organisation. If not, it will create them, save the public key on iCure and save your private & public keys at the local storage location and in the config.ini file.


## What's next ?
Check out our[MedTech Documentation](https://docs.icure.com/sdks/quick-start/python-quick-start) and more particularly our [How To's](https://docs.icure.com/sdks/how-to/index), in order to start implementing new functionalities inside your Python Server!

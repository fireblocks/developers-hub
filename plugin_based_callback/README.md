<p align="center">
  <img src="./logo.svg" width="350" alt="accessibility text">
</p>
<div align="center">

  [Fireblocks Developer Portal](https://developers.fireblocks.com) </br>
  [Fireblocks API Co-Signer & Callback Handler Docs](https://developers.fireblocks.com/reference/automated-signer-callback)
</div>

# Fireblocks Plugin Based Callback Handler
❗⚠️  `This is a WIP Alpha project. Please do not use it in your production environment` ⚠️❗

## Introduction 👋
### Fireblocks API Co-Signer & Callback Handler
The Fireblocks API Co-Signer allows you to automate approvals and signing for transactions and workspace changes. \
This is ideal for any workspace expecting a high volume of transactions, frequent workspace activity, or requiring 24-hour access.\
You can configure the API Co-Signer with a Co-Signer Callback Handler. The Callback Handler is a predefined \HTTPS server that receives requests from the API Co-Signer and returns an action.

When your API Co-Signer is configured with a callback, it sends a POST request to the callback handler. The POST request contains a JSON Web Token (JWT) encoded message signed with the API Co-Signer's private key. The Callback Handler uses the API Co-Signer's public key to verify that every incoming JWT is signed correctly by the API Co-Signer.

The Callback Handler's response is a JWT-encoded message signed with the Callback Handler's private key. This private key must be paired with the public key provided to the API Co-Signer during the Callback Handler's setup.
For detailed documentation of the API Co-Signer Callback Handler Data objects please visit [Fireblocks Developer Portal](https://developers.fireblocks.com/reference/automated-signer-callback).

### Callback Handler Plugin Application
The Fireblocks Plugin Based Callback Handler is a boilerplate application that simplifies the Callback Handler installation and setup for Fireblocks users. \
It is engineered to seamlessly integrate with plugins, allowing users to effortlessly develop custom functionalities without dedicating resources to server application development. The Plugins application is bundled with a selection of pre-configured plugins, each detailed below for reference.

---


## Table Of Contents 📖

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Basic Plugins](https://github.com/fireblocks/developers-hub/blob/main/plugin_based_callback/src/plugins/README.md#basic-plugins-)
  - [Transaction Validation](https://github.com/fireblocks/developers-hub/blob/main/plugin_based_callback/src/plugins/README.md#transaction-validation-plugin-txid_validationpytxidvalidation-class)
  - [Extra Signature Validation](https://github.com/fireblocks/developers-hub/blob/main/plugin_based_callback/src/plugins/README.md#extra-signature-validation-extra_signaturepyextrasignature-class)
  - [Transaction Policy Validation](https://github.com/fireblocks/developers-hub/blob/main/plugin_based_callback/src/plugins/README.md#transaction-policy-validation-plugin-tx_policy_validationpytxpolicyvalidation-class)
- [Contribution](#contribution)
  - [Adding New Plugins](#new-plugins)
  - [New DB Connections](#setting-a-new-db-connection)
- [Usage](#usage)
- [Tests - #TODO]()

---

## Architecture 🏛️
The Plugin Based Callback Handler application is written in Python (3.11). \
Web Framework - FastAPI. 

Co-Signer JWT authentication is implemented in the `authenticate.py`, in `authenticate_jwt` decorator.  
The application assumes that both the Co-Signer public key and the Callback Private key files are located on the server while the path is defined in the .env file.

Plugins that require DB access can use the implemented MongoDB and Postgres integrations. Additional DB interfaces can be implemented by the user - see the 'Contribution' section. 

All exiting plugins and their related code is located in `src/plugins` directory. \
New plugins added by the user can be either located in the `src/plugins` directory (expects by default) or in a different location with the path provided as part of the .env PLUGINS variable.\
The `PLUGINS` env variable should be structured in the following way: \
&emsp; &emsp; `PLUGINS=my_plugin1:/path/to/plugin,my_plugin2` - note that `my_plugin2` is not set with `:path` hence the application assumes that it's in `src/plugins` directory. \
All plugin names should be separated by comma.

All DB interfaces (including new DB interfaces to be added) are located in `src/databases` directory.

Logs configuration can be found in `src/logs/log_config.py` file. \
The log structure is the following: `"module: timestamp | filename:line | level: message"`. 

`settings.py` wraps the environment variables and runs validations (Additional validations - in progress) - the server won't start if the validations fail.

By default, the app is running on port 8000. This can be changed in the `docker-compose.yaml` or in the `APP_LISTENING_PORT` variable in .env file.

---

## Contribution 🤝
### New Plugins:
1. Create a new python file in the `src/plugins` directory and name it in snake_case, for example: `my_example_plugin.py`
3. If you want to place the plugin in a different location - please make sure to update the `PLUGINS` env variable with the path (`my_example_plugin:/path/to/plugin`)
4. Create a class in the newly created file in PascalCase, for example: `MyExamplePlugin`
   - Please make sure to follow the naming convention: `my_example_plugin.py` file name -> `MyExamplePlugin` class name
5. Inherit the abstract class `PluginInterface` from `src/plugins/interface.py`:
```python
from src.plugins.interface import PluginInterface

class MyExamplePlugin(PluginInterface)
.
.
.
```
6. Make sure to implement the required methods:
   - `async def init(self, *args, **kwargs)`: Instantiation function that is being called upon plugin instantiation. Can run any internal logic required for valid object instantiation. 
   - `async _create_db_instance(self, db_type: str)`: Creating a DB instance method, is usually being called in the init method. Declare the method without implementation in plugins that do not require DB access.  
   - `async def process_request(self, data) -> bool`: The entry point to your plugin logic. This method will be called to initiate the plugin approval flow and should return true/false according to the approval decision. 
   - `def __repr__(self)`: Representation for logging purposes
   - `async def set_db_instance(self, db)` - Implemented to set the DB attribute. Can be overridden if required.
7. Update the PLUGINS variable in .env file. Set the name of the plugin in snake_case. In case of running multiple plugins - separate by comma. Don't forget to provide the path to the plugin in case it is not located in `src/plugins`:
   - For example: `PLUGINS=plugin_one,plugin_two,my_example_plugin:/path/to/plugin`
</br>

### Setting a new DB connection:
1. By default, MongoDB and Postgres are supported. If one of these works for you, update the required environment variables in .env file.
2. If a new type of DB connection is required, please follow the steps below:
   - Create a new file in `src/databases`, for example: `my_db_conn.py` 
   - Create a new class in the newly created file and inherit the abstract class `DatabaseInterface` from `src/databases/interface.py`
   ```python
   from src.databases.interface import DatabaseInterface
   
   class MyDbConn(DatabaseInterface):
   .
   .
   . 
   ```
   - Make sure to implement the required methods:
     - `async def _connect(self, *args)`: Initial connection to your DB.
     - `async def _disconnect(self, *args, **kwargs)`: Closing the DB connection.
     - `async def build_query(self, *args, **kwargs)`: Builds the DB query.
     - `async def execute_query(self, *args)`: Executes a query to your DB.
   - Update the `DB_TYPE` variable in the .env file, for example: `DB_TYPE=my_db_conn`
   - Update the `DB_CLASS_MAP` variable in `settings.py` while the key is the DB_TYPE and the value is the name of the DB connection class, for example: 
     ```python
     DB_CLASS_MAP = {
      'my_db_conn': MyDbConn
     }
     ```
--- 

## Usage 🛠
1. Update `.env` file with all the required values (see `example.env` for reference) 
2. Co-Signer public key in a file (To verify received JWT received from the Co-Signer)
3. Callback Handler private key (To sign JWT response back to the Co-Signer)
> **_NOTE:_** Currently the application supports only local keys (both cosigner public and callback private), we recommend to place these in the `src/keys` directory and provide the full path to both in the .env file 
4. With Docker: 
   - Run `docker-compose up`
5. Locally:
   - Run `git clone https://github.com/fireblocks/plugin-based-callback-handler.git`
   - Run `pip install -r requirements.txt`
   - Run `python main.py`
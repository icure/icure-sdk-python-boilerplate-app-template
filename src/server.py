import configparser
import os
from flask import Flask, jsonify
from sdk import init_icure_api

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini"))

app = Flask(__name__)


def init_sdk_with_config():
    public_key = CONFIG["icure"].get("parent_organization_public_key")
    private_key = CONFIG["icure"].get("parent_organization_private_key")
    return init_icure_api(
        CONFIG["icure"]["parent_organization_username"],
        CONFIG["icure"]["parent_organization_token"],
        CONFIG["icure"].get("local_storage_location", "./scratch/localStorage"),
        {public_key: private_key} if public_key is not None and private_key is not None else None
    )


@app.route("/", methods=['GET'])
def entrypoint():
    icure_sdk = init_sdk_with_config()
    parent_user = icure_sdk.user.get_current_user_blocking()
    return jsonify(parent_user.__serialize__())


@app.route("/async", methods=['GET'])
async def async_entrypoint():
    icure_sdk = init_sdk_with_config()
    parent_user = await icure_sdk.user.get_current_user_async()
    return jsonify(parent_user.__serialize__())


if __name__ == "__main__":
    host = CONFIG["icure"].get("host", "127.0.0.1")
    port = CONFIG["icure"].get("port", "3000")
    app.run(host=host, port=int(port), debug=True)

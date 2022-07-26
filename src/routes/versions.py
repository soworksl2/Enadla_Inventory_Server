import json
from os import environ

from flask import Blueprint, Response

import app_constants

versions_BP = Blueprint('versions', __name__)

@versions_BP.route('last_compatible_client_version/', methods=['GET'])
def get_last_compatible_client_version():
    major, minor, patch = app_constants.get_last_compatible_client_version()
    body_response = {
        "last_compatible_client_version": f"{major}.{minor}.{patch}"
    }

    return Response(status=200, response=json.dumps(body_response))
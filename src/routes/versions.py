import json

from flask import Blueprint, Response

import app_constants
from helpers import own_response_factory

versions_BP = Blueprint('versions', __name__)

@versions_BP.route('/last_client_version/', methods=['GET'])
def get_last_client_version():
    major, minor, patch = app_constants.get_last_client_version()

    return own_response_factory.create_json_body(
        status=200,
        last_client_version=f'{major}.{minor}.{patch}'
    )

@versions_BP.route('last_compatible_client_version/', methods=['GET'])
def get_last_compatible_client_version():
    major, minor, patch = app_constants.get_last_compatible_client_version()

    return own_response_factory.create_json_body(
        status=200,
        last_compatible_client_version=f'{major}.{minor}.{patch}'
    )

@versions_BP.route('/backend_version', methods=['GET'])
def get_backend_version():
    current_backend_version= app_constants.get_backend_version()

    return own_response_factory.create_json_body(
        status=200,
        backend_version=current_backend_version
    )
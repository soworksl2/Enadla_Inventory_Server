import json
from os import environ

from flask import Blueprint, Response

versions_BP = Blueprint('versions', __name__)

@versions_BP.route('last_compatible_client_version/', methods=['GET'])
def get_last_compatible_client_version():
    last_compatible_client_version = environ.get('LAST_COMPATIBLE_CLIENT_VERSION', '0.0.0')

    if last_compatible_client_version == '0.0.0':
        body_response = {
            'server_information': 'the last compatible client version was not found'
        }
        return Response(status=500, response=json.dumps(body_response))

    body_response = {
        'last_compatible_client_version': last_compatible_client_version
    }

    return Response(status=200, response=json.dumps(body_response))
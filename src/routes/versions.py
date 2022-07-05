import json
from os import environ

from flask import Blueprint, Response

versionsBlueprint = Blueprint('versions', __name__)

@versionsBlueprint.route('last_compatible_client_version/', methods=['GET'])
def getLastCompatibleClientVersion():
    lastCompatibleClientVersion = environ.get('LAST_COMPATIBLE_CLIENT_VERSION', '0.0.0')

    if lastCompatibleClientVersion == '0.0.0':
        responseBody = {
            'serverInformation': 'the last compatible client version was not found'
        }
        return Response(status=500, response=json.dumps(responseBody))

    responseBody = {
        'lastCompatibleClientVersion': lastCompatibleClientVersion
    }

    return Response(status=200, response=json.dumps(responseBody))
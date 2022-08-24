from flask import Response

from helpers import own_json

def create_json_body(status, server_information = None, error_code = None, **kwargs):
    response_body = {}

    if server_information:
        response_body['server_information'] = server_information

    if error_code:
        response_body['error_code'] = error_code

    for key, value in kwargs.items():
        response_body[key] = value
    
    response_body = own_json.dumps(response_body)
    return Response(status=status, response=response_body, mimetype='application/json')
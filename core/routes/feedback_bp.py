from flask import Blueprint

from core import app_error_code, app_constants
from core.helpers import request_processor
from core.helpers import own_response_factory
from core.database import auth_db_operations, feedback_operations
from core.models import product_feedback

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/product/', methods=['POST'])
def send_product_feedback():
    request_specification = {
        'custom_id_token': {'type': 'string', 'required': True},
        'individual_products_feedback': {'type': 'list', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    try:
        firebase_id_token, custom_claims = auth_db_operations.process_custom_id_token(valid_request['custom_id_token'])
    except app_error_code.InvalidCustomIdTokenException:
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_CUSTOM_ID_TOKEN)
    except Exception:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    if not custom_claims['is_verified']:
        return own_response_factory.create_json_body(409, error_code=app_error_code.UNVERIFIED_USER)

    try:
        decoded_firebase_id_token = auth_db_operations.verify_firebase_id_token(firebase_id_token, True)
    except Exception:
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_ID_TOKEN)

    individual_products_feedback = \
        [product_feedback.IndividualProductFeedback.from_dict(**item) 
        for item in valid_request['individual_products_feedback']]

    #TODO: validate individual_product_feedback before inserting to the database for prevent bad intentions of the users
    #and more secure. Jimy Aguasviva - 20 september 2022

    try:
        feedback_operations.add_individual_products_feedback(decoded_firebase_id_token['uid'], individual_products_feedback)
    except Exception as e:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(200)

@feedback_bp.route('/product/', methods=['GET'])
def get_all_products_feedback_adm():
    request_specification = {
        'api_admin_key': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification, use_slfs=False)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    api_admin_key = valid_request['api_admin_key']

    if api_admin_key != app_constants.get_api_admin_key():
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_API_ADMIN_KEY)

    try:
        products_feedback = feedback_operations.get_all_products_feedback()
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(
        200,
        products_feedback=products_feedback
    )

@feedback_bp.route('/product/', methods=['DELETE'])
def delete_all_products_feedback_adm():
    request_specification = {
        'api_admin_key': {'type': 'string', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification, use_slfs=False)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    api_admin_key = valid_request['api_admin_key']

    if api_admin_key != app_constants.get_api_admin_key():
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_API_ADMIN_KEY)

    try:
        feedback_operations.delete_all_products_feedback()
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(200)
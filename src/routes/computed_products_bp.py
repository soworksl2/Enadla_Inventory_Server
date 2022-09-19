from flask import Blueprint

import app_error_code
import app_constants
from helpers import own_response_factory
from database import computed_products_operations
from helpers import request_processor
from models import computed_products

computed_products_bp = Blueprint('computed_products', __name__)

@computed_products_bp.route('/', methods=['GET'])
def get_last_computed_products():

    #TODO: impplements some authorization method for this endpoind to protect it against
    #competitors. Jimy Aguasviva - 16 september 2022

    try:
        last_computed_products = computed_products_operations.get_last_computed_products()
    except FileNotFoundError:
        return own_response_factory.create_json_body(404, error_code=app_error_code.HTTP_BASIC_ERROR)
    except:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(
        status=200,
        last_computed_products=last_computed_products
    )

@computed_products_bp.route('/', methods=['POST'])
def send_new_computed_products_adm():
    request_specification = {
        'api_admin_key': {'type': 'string', 'required': True},
        'new_computed_products': {'type': 'dict', 'required': True}
    }

    is_valid_request, valid_request = request_processor.parse_request(request_specification, use_slfs=False)

    if not is_valid_request:
        return own_response_factory.create_json_body(400, error_code=app_error_code.HTTP_BASIC_ERROR)

    if not valid_request['api_admin_key'] == app_constants.get_api_admin_key():
        return own_response_factory.create_json_body(401, error_code=app_error_code.INVALID_API_ADMIN_KEY)

    new_computed_products = computed_products.ComputedProducts.from_dict(**valid_request['new_computed_products'])

    try:
        computed_products_operations.push_new_computed_products(new_computed_products)
    except Exception:
        return own_response_factory.create_json_body(400, error_code=app_error_code.UNEXPECTED_ERROR)

    return own_response_factory.create_json_body(200)

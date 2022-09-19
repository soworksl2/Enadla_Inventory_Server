from flask import Blueprint

import app_error_code
from helpers import own_response_factory
from database import computed_products_operations

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
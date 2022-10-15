from flask import Flask

from core.routes import (
    user_info_bp,
    token_information_bp,
    versions,
    shop_bp,
    computed_products_bp,
    feedback_bp
)


def create() -> Flask:
    output = Flask(__name__)

    output.register_blueprint(user_info_bp.user_info_bp, url_prefix='/accounts')
    output.register_blueprint(token_information_bp.token_information_bp, url_prefix='/token_information')
    output.register_blueprint(shop_bp.shop_bp, url_prefix='/shop')
    output.register_blueprint(computed_products_bp.computed_products_bp, url_prefix='/computed_products')
    output.register_blueprint(feedback_bp.feedback_bp, url_prefix='/feedback')
    output.register_blueprint(versions.versions_BP, url_prefix='/versions')

    return output

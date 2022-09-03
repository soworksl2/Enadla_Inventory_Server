from os import environ
from sys import argv

from flask import Flask

app_server = Flask(__name__)

# registering blueprints

from routes import user_info_bp, token_information_bp, versions

app_server.register_blueprint(user_info_bp.user_info_bp, url_prefix='/accounts')
app_server.register_blueprint(token_information_bp.token_information_bp, url_prefix='/token_information')
app_server.register_blueprint(versions.versions_BP, url_prefix='/versions')

#-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-

if __name__ == '__main__':
    is_debug = True if 'DEBUG' in argv else False
    port = int(environ.get('PORT', 8080))
    app_server.run(debug=is_debug, port=port)
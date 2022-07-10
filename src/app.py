from os import environ
from sys import argv

from flask import Flask

app_server = Flask(__name__)

# registering blueprints

from routes import accounts, token_information, versions

app_server.register_blueprint(accounts.accounts_BP, url_prefix='/accounts')
app_server.register_blueprint(token_information.TokenInformation_BP, url_prefix='/tokenInformation')
app_server.register_blueprint(versions.versions_BP, url_prefix='/versions')

#-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-

if __name__ == '__main__':
    is_debug = True if 'DEBUG' in argv else False
    port = int(environ.get('PORT', 8080))
    app_server.run(debug=is_debug, port=port)
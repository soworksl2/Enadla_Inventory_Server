from os import environ
from sys import argv

from flask import Flask

appServer = Flask(__name__)

# registering blueprints

from routes import accounts

appServer.register_blueprint(accounts.accountsBlueprint, url_prefix='/accounts')

#-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-

if __name__ == '__main__':
    isDebug = True if 'DEBUG' in argv else False
    port = int(environ.get('PORT', 8080))
    appServer.run(debug=isDebug, port=port)
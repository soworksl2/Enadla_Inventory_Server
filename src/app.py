from os import environ
from flask import Flask

import firebaseAdmin
appServer = Flask(__name__)

# registering blueprints

from routes import accounts

appServer.register_blueprint(accounts.accountsBlueprint, url_prefix='/accounts')

#-*-*-*-*-*-*-*-*-*-*-*-*-**-*-*-

if __name__ == '__main__':
    port = int(environ.get('PORT', 8080))
    appServer.run(debug=True, port=port)
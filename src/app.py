from os import environ
from sys import argv

from flask import Flask

appServer = Flask(__name__)

@appServer.route('/hola')
def hello():
    return 'hola mundo'

if __name__ == '__main__':
    port = int(environ.get('PORT', 8080))
    appServer.run(debug=True, port=port)
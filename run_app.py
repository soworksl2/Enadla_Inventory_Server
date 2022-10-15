"""
Script to run the aplication
"""

if __name__ == '__main__':
    from os import environ
    from sys import argv

    from core import create_app

    is_debug = True if 'DEBUG' in argv else False
    port = int(environ.get('PORT', 8080))
    create_app.create().run(debug=is_debug, port=port)

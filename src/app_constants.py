"""constants for the application
"""

import os

def get_last_compatible_client_version():
    version_str = os.environ['LAST_COMPATIBLE_CLIENT_VERSION']
    try:
        major, minor, patch = [int(version) for version in version_str.split('.')]
    except:
        raise ValueError('LAST_COMPATIBLE_CLIENT_VERSION')

    if any(version < 0 for version in [major, minor, patch]):
        raise ValueError('LAST_COMPATIBLE_CLIENT_VERSION')

    return (major, minor, patch)
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# --- Exposing firebase module to be able to export from this wrapper 
# (exporting modules from here ensure that the firebase app is initialized)
from firebase_admin import auth
# --- -*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*--*-***--**-*-*--**-*-*-*-*--**--

#TODO: get this key from environment variables instead of hardcoded here
firebase_key_dict = {
  "type": "service_account",
  "project_id": "enadla-inventory-server",
  "private_key_id": "8bdb80ef31a44261f8c54187287bcbc8c0975895",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7N/IQpDvUqzOY\n/N8e88hs7mRbkk2KqdgdwUNIWSL9vibN9JHN0LbPRMip8uKLpaCP+wLVo+fKn738\nOkMCK1jVcVjgebeuAt8btfUFIHzTslaRu2G2XCk/hH6d3RsGw1cLfHr7j/jZBjuz\neVnbP5iW5y4hQZiGtM11rcV2WpsDlmBETb4IytaPNAbXpX6LwbxawnuWtdr+u44x\n0z34hgPjKgWoAd5pBbbNpCB7ubmTKj9CsdXvFcHW0KJUe7rDUFvrlWkvbr82HphL\njMMEupIEtsJ9B1B4TTMGwQrt0BDjOaY5NdL06iWFK769udf4A4pSzm/toikf56BV\nHlvq+3s1AgMBAAECggEAAiTo+Dun9hlThl9yXxHL3ELbB450e2T9v+d9pweNpkom\nJR/gMfMqPij2QwtbALOaqWjRS+jsPRlDwoQDTkl4o2crLVT6NNC9GpLkqxSdFrVD\n7GLbmAxUVPEmRxYSxWrO0CedO/eBPNu8qs32E2lWIiJPLbEpN0pnplRMFD0uPyYA\neVCOdp6FZLeDI4LZqn4PRA02CUpS6SEDC3eptFh+JLloLpR0tlt1kWgioAM2ly/N\nLqsFg+Rmyxo4ewYxYL98s5gU75l8VSCMociSqYf998bBKGcvJrBWSgoCNzpwFJ+X\nIlOPHdTjiL01rrKT8Zan8sFc0xeTLV/v9Ft3I96yIQKBgQDphggKk5o7W71oIYvs\nzTqwCDDQdGS/baMlxPDBO5cmV5YgtKeKDDwRnalepse690PTztFy08li/QuDRTsv\nqZkSFxaUQ1+P/KyjH3vrTIXz+AQauH20AmONKttWvvWsEn0VGDYgN1QLDmEtwxIv\nFwQhECcBcgGPOKd0ZAfDdRRvIQKBgQDNPPf8GiiO9IL54dh6hR9q38dxJul/Hi6L\n50klnuFXD93TDIt8XAwJc0VpapZTZgUL/g2hPSY4plIf6fz1wt/6XKfOdxmGYrnr\ngjqy59EyRAurChWED4oZd2hx6BYA+anOPKUM57TYZTMv8s6M033SOdKFYNv/TY94\nqrakgs4tlQKBgQCohP68kzPT7ipLQRo28wuNCPwhEj26HyaDFRIggB5dnwtJ4tSc\nvKOEmuAk2/p6pAGgkjl3wfosoytxub4ycRNziJHUwKHvyInU1d2ZOgnYu3xKxCSC\niM7KisjqWrfzSwxU8rnsmcDekavzWDiBHvzt1zguxNT3RA0j4yPvG0h5wQKBgA7O\nbzWIzZRCn5BXcr6kC/gx3LmVDRNWohUFwoksRSV6x44KQaXfHh8wabmJLv8lRQfw\ndBtFxhQgK5yRzOYOAQqW1KRYg0bmqHMNGh7+CmGN9ymHuLWmSVg8/RP6olu/pzhx\nt5aOwMU7x82VvsD6IQGhmkZ1DmoEtm0GI9cKeMVhAoGBAOGQ4UATs/cCIp4WqX3c\nlzfrbePQGbCPWSNPuRdzmfekvMKrni0z+J4CzxdzDHSzBMp7BongYnSTZco7DpWb\nOho9bWnmMRbTeaOXX4cg3ZR3AtkVqZTmahw8QDSPTWFn+J6Y/kZRF6U7NkyUJOT8\n9CmhdZGLag0KfPajzJc/RQz3\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-vqx5d@enadla-inventory-server.iam.gserviceaccount.com",
  "client_id": "106541684298115675809",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-vqx5d%40enadla-inventory-server.iam.gserviceaccount.com"
}

firebase_credentials = credentials.Certificate(firebase_key_dict)

firebaseApp = firebase_admin.initialize_app(firebase_credentials)

db = firestore.client()

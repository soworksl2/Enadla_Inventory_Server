"""module with functions to clear tests stuff from the firebase project
"""

from own_firebase_admin import auth, db
from tests.integration_tests.helpers import faker_user_info_data

def clear_tests_from_auth_db():
    """Clean all test user_info from the auth firebase db
    """
    
    user_uids = []

    for email in faker_user_info_data.get_all_test_email():
        try:
            user_record = auth.get_user_by_email(email)
            user_uids.append(user_record.uid)
        except:
            pass
    
    auth.delete_users(user_uids)

def clear_tests_collecion_from_firestore():
    """Clear all tests stuff from the firestore db
    """
    
    test_prefix = 'test_'

    db_batch = db.batch()

    all_db_colections = db.collections()

    for collection in all_db_colections:
        if collection.id.startswith(test_prefix):
            for document in collection.list_documents():
                db_batch.delete(document)

    db_batch.commit()


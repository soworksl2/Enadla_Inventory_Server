"""module with functions to clear tests stuff from the firebase project
"""

from core.own_firebase_admin import auth, db, default_bucket
from tests.integration_tests.helper import faker_user_info_data
from core.database import computed_products_operations

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

#TODO: clear all files that start with test/.
#right now it delete files individually because list_blobs() function doesn't work
#or at least i dont know how it works, in future it should list all files that start with
#test/ and delete it. Jimy Aguas
def clear_tests_from_storage():
    all_computed_products_and_backups_filenames = [
        computed_products_operations.FULL_COMPUTED_PRODUCTS_FILENAME,
        computed_products_operations.FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME,
        computed_products_operations.FULL_DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME]

    all_computed_products_and_backups = [default_bucket.get_blob(filename) for filename in all_computed_products_and_backups_filenames]

    for computed_products_or_backup in all_computed_products_and_backups:
        if computed_products_or_backup is not None:
            computed_products_or_backup.delete()

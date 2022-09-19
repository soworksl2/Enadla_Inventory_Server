from sys import argv

from own_firebase_admin import default_bucket
from helpers import own_json
from models import computed_products

is_debug = 'DEBUG' in argv

COMPUTED_PRODUCTS_BUCKECT_DIRECTORY = 'computed_products' if not is_debug else f'test/computed_products'
COMPUTED_PRODUCTS_FILENAME = 'computed_products.json'
FULL_COMPUTED_PRODUCTS_FILENAME = f'{COMPUTED_PRODUCTS_BUCKECT_DIRECTORY}/{COMPUTED_PRODUCTS_FILENAME}'
BACKUP_COMPUTED_PRODUCTS_FILENAME = 'backup_computed_products.json'
FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME = f'{COMPUTED_PRODUCTS_BUCKECT_DIRECTORY}/{BACKUP_COMPUTED_PRODUCTS_FILENAME}'
DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME = 'deep_backup_computed_products.json'
FULL_DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME = f'{COMPUTED_PRODUCTS_BUCKECT_DIRECTORY}/{DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME}'

def __make_deep_backup_to_current_backup_computed_products():
    current_backup_computed_products = default_bucket.get_blob(FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME)

    if current_backup_computed_products is None:
        return

    current_deep_backup_computed_products = default_bucket.get_blob(FULL_DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME)

    if current_deep_backup_computed_products is not None:
        current_deep_backup_computed_products.delete()

    default_bucket.rename_blob(current_backup_computed_products, FULL_DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME)

def __backup_current_computed_products():
    current_computed_products = default_bucket.get_blob(FULL_COMPUTED_PRODUCTS_FILENAME)

    if current_computed_products is None:
        return

    __make_deep_backup_to_current_backup_computed_products()

    default_bucket.rename_blob(current_computed_products, FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME)

def get_last_computed_products():
    last_computed_products_blob = default_bucket.get_blob(FULL_COMPUTED_PRODUCTS_FILENAME)

    if last_computed_products_blob is None:
        last_computed_products_blob = default_bucket.get_blob(FULL_BACKUP_COMPUTED_PRODUCTS_FILENAME)

    if last_computed_products_blob is None:
        last_computed_products_blob = default_bucket.get_blob(FULL_DEEP_BACKUP_COMPUTED_PRODUCTS_FILENAME)

    if last_computed_products_blob is None:
        raise FileNotFoundError()

    last_computed_products_content = last_computed_products_blob.download_as_bytes().decode('utf-8')
    last_computed_products_deserialized = own_json.loads(last_computed_products_content)

    return computed_products.ComputedProducts.from_dict(**last_computed_products_deserialized)

def push_new_computed_products(new_computed_products: computed_products.ComputedProducts):

    new_computed_products_serialized = own_json.dumps(new_computed_products)

    __backup_current_computed_products()

    new_computed_products_blob = default_bucket.blob(FULL_COMPUTED_PRODUCTS_FILENAME)
    new_computed_products_blob.upload_from_string(new_computed_products_serialized)

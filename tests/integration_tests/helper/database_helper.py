from datetime import datetime
from own_firebase_admin import auth, db
import helper
from helper import faker_user_info_data

def signUp(
            flask_test_client,
            email_number = 1,
            custom_password = '123456',
            custom_machine_creator = 'test_machine1',
            force_is_verified = False):

    new_user = faker_user_info_data.generate_good_user_info(email_number)
    new_user['password'] = custom_password
    new_user['extra_info']['creator_machine'] = custom_machine_creator

    request_body = helper.process_and_add_slfs({
        'user_info': new_user
    })

    r = flask_test_client.post('/accounts/', json=request_body)
    uid = r.json['updated_user_info']['uid']

    if force_is_verified:
        auth.update_user(uid, email_verified = True)

    return uid

def authenticate(flask_test_client, email_number = 1, custom_password = '123456', custom_machine_id = 'test_machine1'):
    request_body = helper.process_and_add_slfs({
        'machine_id': custom_machine_id,
        'email': faker_user_info_data.get_test_email(email_number),
        'password': custom_password
    })

    r = flask_test_client.get('/accounts/auth/', json=request_body)

    if not r.status_code == 200:
        raise Exception(f'the authentication is invalid the error code is: {r.json["error_code"]}')

    return (r.json['custom_id_token'], r.json['refresh_token'], r.json['user_info'])

def change_date_of_machine_link(machine_id, new_date):
    if not isinstance(new_date, datetime):
        raise TypeError('new_date should be a datetime')

    machine_links_founds = db.collection('test_machine_links').where('machine_id', '==', machine_id).get()

    if len(machine_links_founds) <= 0:
        raise Exception(f'the machine_link for the machine {machine_id} was not found in test_machine_links collecion')

    machine_links_founds[0].reference.update({
        'link_creation_date': new_date
    })
    
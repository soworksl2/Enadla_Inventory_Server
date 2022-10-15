#TODO: this module uses a lot of calls in firestore that can be avoided, I have to change it to use cached data without change the api

from sys import argv
from datetime import datetime, timedelta

import pytz

from core import app_error_code, app_constants
from core.own_firebase_admin import db
from core.models import machine_link

#region Collection names as CN
is_debug = 'DEBUG' in argv

CN_MACHINE_LINKS = 'machine_links' if not is_debug else 'test_machine_links'
#endregion

def force_delete_link(machine_id):
    raise NotImplementedError()

def __create_new_link(machine_id, email):
    if not machine_id or not email:
        raise ValueError('machine_id and email should not be empty or null')

    machine_links_founds = db.collection(CN_MACHINE_LINKS).where('machine_id', '==', machine_id).get()
    new_machine_link = machine_link.MachineLink(
        machine_id=machine_id,
        email_linked=email,
        link_creation_date=datetime.now(tz=pytz.utc))

    if len(machine_links_founds) <= 0:        
        db.collection(CN_MACHINE_LINKS).add(new_machine_link.__dict__)
    elif not machine_links_founds[0].get('email_linked') == email:
        __update_link(machine_id, email)
    else:
        pass

def __update_link(machine_id, email):
    if not machine_id or not email:
        raise ValueError('machine_id and email cannot be null or empty')

    machine_links_founds = db.collection(CN_MACHINE_LINKS).where('machine_id', '==', machine_id).get()

    if len(machine_links_founds) <= 0:
        raise Exception('was not machine links founds and cannot update nothing')

    new_machine_link = machine_link.MachineLink(
        machine_id=machine_id,
        email_linked=email,
        link_creation_date=datetime.now(tz=pytz.utc)
    )

    if machine_links_founds[0].get('email_linked') == email:
        machine_links_founds[0].reference.set(new_machine_link.__dict__)
    elif not is_locked(machine_id):
        machine_links_founds[0].reference.set(new_machine_link.__dict__)
    else:
        raise app_error_code.LockedMachineException()

def create_link(machine_id, email):
    
    if not machine_id or not email:
        raise ValueError('machine_id or email cannot be empty or null')

    machine_links_founds = db.collection(CN_MACHINE_LINKS).where('machine_id', '==', machine_id).get()

    if len(machine_links_founds) <= 0:
        __create_new_link(machine_id, email)

    email_locker = get_locker(machine_id)

    if email_locker is None:
        __create_new_link(machine_id, email)
    elif email_locker == email:
        pass
    else:
        raise app_error_code.LockedMachineException()

def is_locked(machine_id):
    machine_link_time_locked = app_constants.get_machine_link_locked_time()

    machine_links_founds = db.collection(CN_MACHINE_LINKS).where('machine_id', '==', machine_id).get()

    if len(machine_links_founds) <= 0:
        return False

    unlocked_date = machine_links_founds[0].get('link_creation_date') + timedelta(days=machine_link_time_locked)

    return datetime.now(tz=pytz.utc) < unlocked_date

def get_locker(machine_id):
    machine_link_time_locked = app_constants.get_machine_link_locked_time()

    machine_links_founds = db.collection(CN_MACHINE_LINKS).where('machine_id', '==', machine_id).get()

    if len(machine_links_founds) <= 0:
        return None

    linked_email = machine_links_founds[0].get('email_linked')
    unlocked_date = machine_links_founds[0].get('link_creation_date') + timedelta(days=machine_link_time_locked)

    if datetime.now(tz=pytz.utc) < unlocked_date:
        return linked_email
    else:
        return None



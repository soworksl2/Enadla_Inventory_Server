"""offers function to get fake userInfo data
"""

MIN_EMAIL_TEST_NUMBER = 1
MAX_EMAIL_TEST_NUMBER = 10

def get_test_email(number):
    """return an valid test email

    Args:
        number (int): the number of the email

    Raises:
        TypeError: if the number is not an integer 
        ValueError: if the number is not in the range between MIN_EMAIL_TEST_NUMBER and MAX_EMAIL_TEST_NUMBER

    Returns:
        str: the valid test email with the correspond number
    """

    if not isinstance(number, int):
        raise TypeError('number should be an integer')

    if number < MIN_EMAIL_TEST_NUMBER or number > MAX_EMAIL_TEST_NUMBER:
        raise ValueError(f'number should be in a range from {MIN_EMAIL_TEST_NUMBER} to {MAX_EMAIL_TEST_NUMBER}')

    return f'enadla.inventory.test{number}@gmail.com'

def get_all_test_email():
    """return a generator with all valid test emails

    Yields:
        str: the test valid emails
    """

    for i in range(MIN_EMAIL_TEST_NUMBER, MAX_EMAIL_TEST_NUMBER + 1):
        yield get_test_email(i)

def generate_good_user_info(email_number=1):
    return {
        'email': get_test_email(email_number),
        'password': '123456',
        'owner_name': 'test',
        'extra_info': {
            'creator_machine': 'test_machine'
        }
    }
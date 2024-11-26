import random
import string


def generate_password():
    length = 8
    all_characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(all_characters) for _ in range(length))

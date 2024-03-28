import string
import random


def gen_random_id(length):
    idstr = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return idstr

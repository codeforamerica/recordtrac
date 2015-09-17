"""
    public_records_portal.gravatar
    ~~~~~~~~~~~~~~~~

    Implements gravatar helper functions

"""



# import code for encoding urls and generating md5 hashes
import hashlib


def get_gravatar_url(email):
    email = email.lower()
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?d=blank"
    return gravatar_url

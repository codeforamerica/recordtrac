"""
    public_records_portal.spam
    ~~~~~~~~~~~~~~~~

    Implements spam filters used on RecordTrac's forms that don't require login. Akismet is a dependency (https://akismet.com) and the following environment variables need to be set in order for this to work: AKISMET_KEY, APPLICATION_URL

"""

from flask.ext.login import current_user

import akismet
from public_records_portal import app


def check_for_spam():
    if current_user.is_authenticated:  # Spam filter is currently implemented to prevent bot spamming, so if someone is logged in they have already verified they are human
        return False
    if app.config[
        'ENVIRONMENT'] == 'PRODUCTION':  # This only needs to work in production, unless a local config variable is set to indicate otherwise
        return True
    elif 'CHECK_FOR_SPAM' in app.config:
        return True
    return False


def is_spam(comment, user_ip, user_agent):
    if check_for_spam():
        app.logger.info("\n\nAttempting to check for spam...")
        key = app.config['AKISMET_KEY']
        blog = app.config['APPLICATION_URL']
        if not is_working_akismet_key(key=key, blog=blog):
            app.logger.info("\n\nThere was a problem verifying the supplied AKISMET_KEY. Unable to check for spam.")
            return False
        if isinstance(comment, unicode):
            comment = comment.encode('utf8', 'ignore')
        if akismet.comment_check(key=key, blog=blog, user_ip=user_ip, user_agent=user_agent,
                                 comment_content=comment) or 'http' in comment:
            app.logger.info("Spam detected: %s" % comment)
            return True
    return False


def is_working_akismet_key(key, blog):
    key = app.config['AKISMET_KEY']
    blog = app.config['APPLICATION_URL']
    return akismet.verify_key(key=key, blog=blog)

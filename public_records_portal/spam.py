from public_records_portal import app
import akismet
import logging


def check_for_spam():
	if app.config['ENVIRONMENT'] == 'PRODUCTION':
		return True
	elif 'CHECK_FOR_SPAM' in app.config:
		return True
	return False

def is_spam(comment, user_ip, user_agent):
	if check_for_spam():
		app.logger.info("\n\nAttempting to check for spam...")
		key = app.config['AKISMET_KEY']
		blog = app.config['APPLICATION_URL']
		if not is_working_akismet_key(key = key, blog = blog):
			app.logger.info("\n\nThere was a problem verifying the supplied AKISMET_KEY. Unable to check for spam.")
			return False
		if isinstance(comment, unicode):
			comment = comment.encode('utf8', 'ignore')
		if akismet.comment_check(key = key, blog = blog, user_ip = user_ip, user_agent = user_agent, comment_content = comment) or 'http' in comment:
			app.logger.info("Spam detected: %s" % comment )
			return True
	return False

def is_working_akismet_key(key, blog):
	key = app.config['AKISMET_KEY']
	blog = app.config['APPLICATION_URL']
	return akismet.verify_key(key=key, blog=blog)
from public_records_portal import app
import akismet
import logging

# Set flags:

check_for_spam = True
if app.config['ENVIRONMENT'] == 'PRODUCTION':
	check_for_spam = True


def is_spam(comment):
	if check_for_spam:
		key = app.config['AKISMET_KEY']
		blog = app.config['APPLICATION_URL']
		if isinstance(comment, unicode):
			comment = comment.encode('utf8', 'ignore')
		if akismet.comment_check(key = key, blog = blog, user_ip = '127.0.0.1', user_agent = 'Mozzila/5.0 (...) Gecko/20051111 Firefox/1.5', comment_content = comment) or 'http' in comment:
			app.logger.info("Spam detected: %s" % comment )
			return True
	return False

def is_working_akismet_key():
	key = app.config['AKISMET_KEY']
	blog = app.config['APPLICATION_URL']
	return akismet.verify_key(key=key, blog=blog)
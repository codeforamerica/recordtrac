from public_records_portal import app
import akismet

def is_spam(comment):
	key = app.config['AKISMET_KEY']
	blog = app.config['APPLICATION_URL']
	if isinstance(comment, unicode):
		comment = comment.encode('utf8', 'ignore')
	if akismet.comment_check(key = key, blog = blog, user_ip = '127.0.0.1', user_agent = 'Mozzila/5.0 (...) Gecko/20051111 Firefox/1.5', comment_content = comment) or 'http' in comment:
		return True
	return False

def is_working_akismet_key():
	key = app.config['AKISMET_KEY']
	blog = app.config['APPLICATION_URL']
	return akismet.verify_key(key=key, blog=blog)
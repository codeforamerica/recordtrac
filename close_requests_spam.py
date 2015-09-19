import sys
from public_records_portal import models, prr

arg_length = len(sys.argv)
if arg_length != 4:
	print 'Enter your user_id followed by the first request_id and the last request_id'
else:
	user_id = sys.argv[1]
	u = models.User.query.get(user_id)
	if u:
		begin = int(sys.argv[2])
		end = int(sys.argv[3])
		if begin < end:
			for request_id in range(begin, end + 1):
				print "Closing request %s" %(request_id)
				prr.close_request_spam(user_id = user_id, request_id = request_id)
			print 'Successfully closed requests %s to %s' %(begin, end)
		else:
			'The range you entered is invalid. Please enter a valid range.'
	else:
		print 'You entered %s for a user_id, which does not exist. Please enter a valid user_id' %(user_id)




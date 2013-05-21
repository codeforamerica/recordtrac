def note_added(city_employee):
	return "A note has been added to your request by %s" %(city_employee), "Your note has been added."

def record_added(city_employee):
	return "A record has been added to your request by %s" %(city_employee), "Your record has been uploaded."

def request_routed(city_employee):
	return "Your request has been rerouted.", "%s has routed this public records request to you." %(city_employee)

def question_added(city_employee):
	return "Your public records request needs clarification.", "Your question has been submitted."

def request_submitted(request_text, city_employee, phone_number):
	subject_line = "Thank you for your request!"
	email_body = "<p>Thank you for submitting your public records request. You can find a copy of your message below:</p></br> %s </br><p>You can always review this message and our future response to your request, by clicking here.</p><p>In the future, you may have to answer questions about your record requests. These questions are designed to help the City understand the type of information you need and help them quickly provide you with your documents. If your record exists, you will receive an email notifying you that your record was posted online.</p><p>If you have any questions, feel free to send a message to %s by clicking here or calling %s.</p>" %(request_text, city_employee, phone_number)
	return subject_line, email_body

def request_submitted_city(request_text):
	subject_line = "A public records request has been sent to you."
	email_body = "<p>A public records request has been assigned to you. The full text of the request can be viewed below:</p></br> %s </br><p>Click here to view more details.</p><p>You have the option to: <ul> <li> Route the request to another city employee who you believe owns the record </li> <li> Ask the person who requested the record more questions </li> <li> Immediately respond with the requested record </li> <li> Ask for an extension </li> </ul></p>" %(request_text)
	return subject_line, email_body

# def request_routed(city_employee, phone_number, request_text):
# 	subject_line = "An update on your public records request"
# 	email_body = "<p>Your public records request has been sent to %s, who is responsible for sending you the information you need.</p><p>If you have any questions or concerns, feel free to send a message to %s by clicking here or calling %s. You can read the full text of your records request below:</p><p></br>%s</br></p>" %(city_employee, phone_number, request_text)
# 	return subject_line, email_body

def request_routed_city(city_employee, note, request_text, date, number):
	subject_line = "You have been sent a public records request"
	email_body = "<p>%s sent you a public records request.  You received this notice because %s believed you are the best person to answer this request and wrote:</p></br> %s </br><p>You can read the full records requests that was submitted on %s below.</p></br> %s </br> <p>The City has %s more business days to respond to the request before being in violation of the California Public Records Act. Click here to view all of the details about the records request. You have the option to:<ul><li>Route the request to another city employee who you believe owns the record</li><li>Ask the person who requested the record more questions</li><li>Immediately respond with the requested record</li><li>Ask for an extension</li></ul></p>" % (city_employee, note, request_text, date, number)
	return subject_line, email_body

def request_fulfilled(city_employee):
	subject_line = "Your records have been posted online"
	email_body = "<p>The records you requested have been posted online. You can download all of the documents by clicking here.</p><p>Information may have been removed from the documents you requested to protect the privacy or identity of another individual. If you have any questions or concerns, you can send a message to %s by clicking here." %(city_employee)
	return subject_line, email_body

def request_fulfilled_city(city_employee, request_text, date):
	subject_line = "Public Records Request Fulfilled"
	email_body = "<p>%s fulfilled the following public records request submitted on %s:</p></br>%s</br><p>Click here to view the filled request. If you believe the request is not complete and need to upload additional documents, you can do that at the link provided.</p>" %(city_employee, request_text, date)
	return subject_line, email_body

def request_rejected_norecord(city_employee, phone_number):
	subject_line = "Your public records request was rejected"
	email_body = "<p>The City of Oakland is unable to send you the documents you requested. The documents requested do not exist.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, phone_number)
	return subject_line, email_body

def request_rejected_otherorg(city_employee, other_org, phone_number):
	subject_line = "Your public records request was rejected"
	email_body = "<p>The City of Oakland is unable to send you the documents you requested. The City does not have the records you want.  Contact %s if you want copies of those records.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, other_org, phone_number)
	return subject_line, email_body

def request_rejected_privacy(city_employee, phone_number):
	subject_line = "Your public records request was rejected"
	email_body = "<p>The City of Oakland is unable to send you the documents you requested. The California Public Records Act prohibits the City from providing you with a person's employment, medical, or similar files to protect their privacy.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, phone_number)
	return subject_line, email_body

def request_rejected_lawsuit(city_employee, phone_number):
	subject_line = "Your public records request was rejected"
	email_body = "<p>The City of Oakland is unable to send you the documents you requested. The California Public Records Act prohibits the City from releasing records related to an on-going lawsuit.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, phone_number)
	return subject_line, email_body

def request_rejected_investigation(city_employee, phone_number):
	subject_line = "Your public records request was rejected"
	email_body = "<p>The City of Oakland is unable to send you the documents you requested. The California Public Records Act prohibits the City from releasing investigative records for crimes committed or police incident reports, rap sheets, and arrest records.  Contact %s if you want copies of those records.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, phone_number)
	return subject_line, email_body

def request_withdrawn(city_employee, phone_number):
	subject_line = "Your public records request has been closed"
	email_body = "<p>The City of Oakland understands that you no longer need the requested records.</p><p><ul>If you are unsatisfied, you can do the following:<li>Send %s a message by clicking here or calling %s to speak with them directly.</li><li>File a complaint with the Public Ethics Commission.</li></ul></p>" %(city_employee, phone_number)
	return subject_line, email_body


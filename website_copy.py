def request_submitted(request_text, city_employee, phone_number):
	subject_line = "Thank you for your request!"
	email_body = "Thank you for submitting your public records request. You can find a copy of your message below:</br> %s </br> You can always review this message and our future response to your request, by clicking here. In the future, you may have to answer questions about your record requests. These questions are designed to help the City understand the type of information you need and help them provide you with the . If your record exists, you will receive an email notifying you that your record was posted online. </br> If you have any questions, feel free to send a message to %s by clicking here or calling %s. " %(request_text, city_employee, phone_number)
	return subject_line, email_body

def request_submitted_city(request_text):
	subject_line = "Request for Public Records"
	email_body = "A public records request has been sent to you. The full text of the request can be found below:</br> %s </br> Click here to receive more details. You have the option to: <ul> <li> Route the request to another city employee who you believe owns the record </li> <li> Ask the person who requested the record more questions </li> <li> Immediately respond with the requested record </li> <li> Ask for an extension </li> </ul>" %(request_text)
	return subject_line, email_body
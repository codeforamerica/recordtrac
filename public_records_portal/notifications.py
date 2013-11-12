from datetime import datetime, timedelta
from public_records_portal import app
import os
import json
from db_helpers import *
from departments import *
import sendgrid
from flask import render_template

# Set flags:

send_emails = False
test = "[TEST] "
if app.config['ENVIRONMENT'] == 'PRODUCTION':
	send_emails = True
	test = ""

### @export "generate_prr_emails"
def generate_prr_emails(request_id, notification_type, user_id = None):
	app_url = app.config['APPLICATION_URL'] 
	# Define the e-mail template:
	template = "generic_email.html" 
	if notification_type == "Request made":
		template = "new_request_email.html"
	# Get information on who to send the e-mail to and with what subject line based on the notification type:
	email_info = get_email_info(notification_type=notification_type)
	email_subject = "Public Records Request %s: %s" %(request_id, email_info["Subject"])
	recipient_types = email_info["Recipients"]
	include_unsubscribe_link = True
	unfollow_link = None 
	for recipient_type in recipient_types:
		if user_id and (recipient_type == "Requester" or recipient_type == "Subscriber"):
			subscriber = get_subscriber(request_id = request_id, user_id = user_id)
			should_notify = get_attribute(attribute = "should_notify", obj = subscriber)
			if should_notify == False:
				print "Person unsubscribed, no notification sent."
				continue
		page = "%srequest/%s" %(app_url,request_id) # The request URL 
		if "Staff" in recipient_type:
			page = "%scity/request/%s" %(app_url,request_id)
			include_unsubscribe_link = False # Gets excluded for city staff
		else:
			unfollow_link = "%sunfollow/%s/" %(app_url, request_id)
			if notification_type == "Request closed":
				page = "%sfeedback/request/%s" %(app_url,request_id)
		if recipient_type in ["Staff owner","Requester","Subscriber","Staff participant"]:
			if user_id:
				recipient = get_attribute(attribute = "email", obj_id = user_id, obj_type = "User")
				# if recipient_type != "Subscriber" or get_attribute(attribute="")
				if recipient:
					if unfollow_link:
						unfollow_link = unfollow_link + recipient
					send_prr_email(page = page, recipients = [recipient], subject = email_subject, template = template, include_unsubscribe_link = include_unsubscribe_link, unfollow_link = unfollow_link)
			else:
				print "Can't send an e-mail out if no user exists."
		elif recipient_type == "Subscribers":
			subscribers = get_attribute(attribute = "subscribers", obj_id = request_id, obj_type = "Request")
			for subscriber in subscribers:
				if subscriber.should_notify == False:
					print "Person unsubscribed, no notification sent."
					continue
				recipient = get_attribute(attribute = "email", obj_id = subscriber.user_id, obj_type = "User")
				if recipient:
					if unfollow_link:
						unfollow_link = unfollow_link + recipient
					send_prr_email(page = page, recipients = [recipient], subject = email_subject, template = template, include_unsubscribe_link = include_unsubscribe_link, unfollow_link = unfollow_link) # Each subscriber needs to get a separate e-mail.
		elif recipient_type == "Staff participants":
			recipients = []
			participants = get_attribute(attribute = "owners", obj_id = request_id, obj_type = "Request")
			for participant in participants:
				recipient = get_attribute(attribute = "email", obj_id = participant.user_id, obj_type = "User")
				if recipient:
					recipients.append(recipient)
			send_prr_email(page = page, recipients = recipients, subject = email_subject, template = template, include_unsubscribe_link = include_unsubscribe_link, cc_everyone = False, unfollow_link = unfollow_link)
		else:
			print recipient_type
			print "Not a valid recipient type"

### @export "send_prr_email"
def send_prr_email(page, recipients, subject, template, include_unsubscribe_link = True, cc_everyone = False, password = None, unfollow_link = None):
	if recipients:
		if send_emails:
			try:
				send_email(body = render_template(template, unfollow_link = unfollow_link, logo_url = "%sstatic/images/CityTree_logo_green.jpg" %(app.config['APPLICATION_URL'] ), page = page, password = password), recipients = recipients, subject = subject, include_unsubscribe_link = include_unsubscribe_link, cc_everyone = cc_everyone)
			except:
				print "E-mail was not sent."
		else:
			print "%s to %s with subject %s" % (render_template(template, page = page), recipients, subject)

### @export "send_email"
def send_email(body, recipients, subject, include_unsubscribe_link = True, cc_everyone = False):
	mail = sendgrid.Sendgrid(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'], secure = True)
	sender = app.config['DEFAULT_MAIL_SENDER']
	plaintext = ""
	html = body
	message = sendgrid.Message(sender, subject, plaintext, html)
	if not include_unsubscribe_link:
		message.add_filter_setting("subscriptiontrack", "enable", 0)
	if cc_everyone: # Not being used for now
		message.add_to(recipients[0])
		for recipient in recipients:
			# if should_notify(recipient):
				message.add_cc(recipient)
	else:
		for recipient in recipients:
			# if should_notify(recipient):
				message.add_to(recipient)
	message.add_bcc(sender)
	mail.web.send(message)

### @export "due_date"
def due_date(date_obj, extended = None, format = True):
	days_to_fulfill = 10
	if extended == True:
		days_to_fulfill = days_to_fulfill + 14
	if not date_obj:
		return None
	if type(date_obj) is not datetime:
		date_obj = datetime.strptime(date_obj, "%Y-%m-%dT%H:%M:%S.%f")
	due_date = date_obj + timedelta(days = days_to_fulfill)
	if format:
		return format_date(due_date.date())
	return due_date.date()

### @export "is_due_soon"
def is_due_soon(date_obj, extended = None):
	current_date = datetime.now().date()
	due = due_date(date_obj = date_obj, extended = extended, format = False)
	num_days = 2
	if not (current_date >= due): # if not overdue
		if (current_date + timedelta(days = num_days)) >= due:
			return True, due
	return False, due

### @export "is_overdue"
def is_overdue(date_obj, extended = None):
	current_date = datetime.now().date()
	due = due_date(date_obj = date_obj, extended = extended, format = False)
	if (current_date >= due):
		return True, due
	return False, due

### @export "get_email_info"
def get_email_info(notification_type):
	email_json = open(os.path.join(app.root_path, 'static/json/emails.json'))
	json_data = json.load(email_json)
	return json_data["Notification types"][notification_type]

### @export "notify_due"
def notify_due():
	requests = get_objs("Request")
	email_json = open(os.path.join(app.root_path, 'static/json/emails.json'))
	json_data = json.load(email_json)
	for req in requests:
		if "Closed" not in req.status:
			# Check if it is due in 2 days
			due_soon, date_due = is_due_soon(req.date_created, req.extended) 
			if due_soon:
				change_request_status(req.id, "Due soon")
				email_subject = "%sPublic Records Request %s: %s" %(test, req.id, json_data["Notification types"]["Request due"])
			else:
				# Otherwise, check if it is overdue
				overdue, date_due = is_overdue(req.date_created, req.extended)
				if overdue:
					change_request_status(req.id, "Overdue")
					email_subject = "%sPublic Records Request %s: %s" %(test, req.id, json_data["Notification types"]["Request overdue"]["Subject"])
				else:
					continue
			recipients = get_staff_recipients(req)
			app_url = app.config['APPLICATION_URL']
			page = "%scity/request/%s" %(app_url,req.id)
			body = "You can view the request and take any necessary action at the following webpage: <a href='%s'>%s</a>.</br></br> This is an automated message. You are receiving it because you are listed as the Public Records Request Liaison, Backup or Supervisor for your department." %(page, page)
				# Need to figure out a way to pass in generic email template outside application context. For now, hardcoding the body.
			send_email(body = body, recipients = recipients, subject = email_subject, include_unsubscribe_link = False)

### @export "get_staff_recipients"
def get_staff_recipients(request):
	recipients = []
	owner_email = get_owner_data(request.id, attributes=["email"])[0]
	recipients.append(owner_email)
	# Look up the department for the request, and get the contacts and backup:
	dept = get_dept_by_request(request)
	if dept:
		contact_email = get_contact_by_dept(dept)
		if contact_email and contact_email not in recipients:
			recipients.append(contact_email)
		backup_email = get_backup_by_dept(dept)
		if backup_email and backup_email not in recipients:
			recipients.append(backup_email)
	if recipients:
		return recipients
	return None

### @export "should_notify"
def should_notify(user_email):
	""" Looks up the user in do_not_email.json and returns False if found. """
	do_not_email = open(os.path.join(app.root_path, 'static/json/do_not_email.json'))
	json_data = json.load(do_not_email)
	for department in json_data:
		emails = json_data[department]['Emails']
		for email in emails:
			if email.lower() == user_email.lower():
				return False
	return True

### @export "format_date"
def format_date(obj):
	""" Take a datetime object and return it in format Jun 12, 2013 """
	return obj.strftime('%b %d, %Y')



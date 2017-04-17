#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    public_records_portal.notifications
    ~~~~~~~~~~~~~~~~

    Implements e-mail notifications for RecordTrac. Flask-mail is a dependency, and the following environment variables
    need to be set in order for this to work: MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD,
    and DEFAULT_MAIL_SENDER.

"""

import json
import mimetypes
import os
import urllib

from flask import render_template
from flask_mail import Mail, Message

import helpers
from db_helpers import *

# Set flags:

send_emails = False
test = '[TEST] '
template_prefix = 'email_templates/'
if app.config['SEND_EMAILS']:
    send_emails = True
    test = ''


def generate_prr_emails(
    request_id,
    notification_type,
    notification_content
    ):
    # 'text=None' is used additional information.
    # 'text2=None' is used if there are more variable text passed into email such as with 'close this request' and being offered multiple reasons
    if 'user_id' not in notification_content:
        notification_content['user_id']=None
    app.logger.info('''
                    Generating e-mails for request with ID: %s, notification type: %s, and user ID: %s'''
                    % (request_id, notification_type, notification_content['user_id']))

    agency_app_url = app.config['AGENCY_APPLICATION_URL']
    public_app_url = app.config['PUBLIC_APPLICATION_URL']
    template = template_prefix + 'email_%s.html' % (notification_type)
    # making a new request
    #
    # if notification_type == 'Request made':
    #     template = 'emtemplate_new_request.html'
    #
    # elif notification_type == 'Question asked':
    # # asking a question
    #
    #     template = 'emtemplate_question_asked.html'
    # elif notification_type == 'Question answered':
    #
    # # respond to question
    #
    #     template = 'emtemplate_question_answered.html'
    # elif notification_type == 'City response added':
    #     template = 'emtemplate_city_response_added.html'
    # elif notification_type == 'Public note added':
    #
    # # adding a note
    #
    #     template = 'emtemplate_public_note_added.html'
    # elif notification_type == 'Request assigned':
    #
    # # Changing Assignee
    #
    #     template = 'emtemplate_request_assigned.html'
    # elif notification_type == 'Request closed':
    #
    # # Closing a request
    #
    #     template = 'emtemplate_request_closed.html'
    # elif notification_type == 'Staff participant added':
    #
    # # Adding a helper
    #     # user = User.query.get(user_id)
    #     # user_name = user.alias
    #
    #     text = text['owner_reason']
    #     template = 'emtemplate_helper_added.html'
    # elif notification_type == 'Helper removed':
    #
    # # Removing a helper
    #
    #     template = 'emtemplate_helper_removed.html'
    # elif notification_type == 'Acknowledge request':
    #
    # # Acknowledging a Request
    #
    #     template = 'emtemplate_acknowledge_request.html'
    # elif notification_type == 'Reopen request':
    #
    # # Reopening a request
    #
    #     template = 'emtemplate_reopen_request.html'
    # elif notification_type == 'Nonportal agency':
    #
    # # Nonportal request for agency user
    #
    #     template = 'email_nonportal_agency.html'
    # elif notification_type == 'Nonportal requester':
    #
    # # Nonportal request for requster
    #
    #     template = 'emtemplate_nonportal_requester.html'
    # elif notification_type == 'Extend request':
    #
    # # Extending a request
    #
    #     if 'days_after' in notification_content:
    #         if notification_content['days_after'] is not None:
    #             days_after = notification_content['days_after']
    #             additional_information = notification_content['additional_information']
    #     template = 'emtemplate_extend_request.html'
    # elif 'Public Notification Template' in notification_type:
    #     template = 'system_email_' + notification_type[-2:] + '.html'
    # elif 'Agency Notification Template' in notification_type:
    #     template = 'agency_email_' + notification_type[-2:] + '.html'

    # Handles emails for nonportal agencies

    if "email_non-portal-agency_agency.html" in template:
        send_prr_email(
            page=None,
            recipients=[notification_content['recipient']],
            template=template,
            notification_content=notification_content,
            subject='OpenRecords Portal Request regarding ' + notification_content['text']['request_summary'],
            )
        return True
    elif 'email_non-portal-agency_requester.html' in template:
        send_prr_email(
            page=None,
            recipients=[notification_content['recipient']],
            template=template,
            notification_content=notification_content,
            subject='Your request to ' + notification_content['department'].name + ' regarding '
                 + notification_content['text']['request_summary'],
            )
        return True

    # Get information on who to send the e-mail to and with what subject line based on the notification type:

    email_info = get_email_info(notification_type=notification_type)
    email_subject = 'Public Records Request %s: %s' % (request_id,
    email_info['Subject'])
    recipient_types = email_info['Recipients']
    include_unsubscribe_link = True
    unfollow_link = None

    # Special case for when the nonportal agency is contacted

    # if recipient_types is None:
    #     if template in 'emtemplate_nonportal_agency.html':
    #         send_prr_email(
    #             page=None,
    #             recipients=notification_content['recipient'],
    #             template=template,
    #             notification_content=notification_content,
    #             subject='OpenRecords Portal Request regarding '
    #                 + notification_content['text']['request_summary']
    #             )
    #     elif template in 'emtemplate_nonportal_requester.html':
    #         send_prr_email(
    #             page=None,
    #             recipients=notification_content['recipient'],
    #             template=template,
    #             notification_content=notification_content,
    #             subject='Your request to ' + notification_content['department']
    #                 + ' regarding ' + notification_content['text']['request_sumamry'],
    #             )

    if notification_content['user_id']:
        user_id = notification_content['user_id']
    else:
        user_id = None

    for recipient_type in recipient_types:
        # Skip anyone that has unsubscribed
        if user_id and (recipient_type == 'Requester' or recipient_type
                        == 'Subscriber'):
            subscriber = get_subscriber(request_id=request_id,
                    user_id=user_id)
            should_notify = get_attribute(attribute='should_notify',
                    obj=subscriber)
            if not should_notify:
                if not subscriber:
                    continue
                else:
                    app.logger.info('''

Subscriber %s unsubscribed, no notification sent.'''
                                    % subscriber.id)
                    continue

        # Set up the e-mail

        page = '%srequest/%s' % (public_app_url, request_id)  # The request URL
        if 'Staff' in recipient_type:
            page = '%scity/request/%s' % (agency_app_url, request_id)
            include_unsubscribe_link = False  # Gets excluded for city staff
        else:
            unfollow_link = '%sunfollow/%s/' % (public_app_url,
                    request_id)
            if notification_type == 'Request closed':
                page = '%sfeedback/request/%s' % (public_app_url,
                        request_id)

        if recipient_type in ['Staff owner', 'Requester', 'Subscriber',
                              'Staff participant']:
            if user_id:
                recipient = get_attribute(attribute='email',
                        obj_id=user_id, obj_type='User')

                # if recipient_type != "Subscriber" or get_attribute(attribute="")

                if recipient:
                    if unfollow_link:
                        unfollow_link = unfollow_link + recipient
                    send_prr_email(
                        page=page,
                        recipients=[recipient],
                        subject=email_subject,
                        template=template,
                        include_unsubscribe_link=include_unsubscribe_link,
                        unfollow_link=unfollow_link,
                        notification_content=notification_content
                        )
            else:
                app.logger.debug('''

 No user ID provided''')
        elif recipient_type == 'Subscribers':
            subscribers = get_attribute(attribute='subscribers',
                    obj_id=request_id, obj_type='Request')
            for subscriber in subscribers:
                if subscriber.should_notify == False:
                    app.logger.info('''

 Subscriber %s unsubscribed'''
                                    % subscriber.id)
                    continue
                recipient = get_attribute(attribute='email',
                        obj_id=subscriber.user_id, obj_type='User')
                if recipient:
                    if unfollow_link:
                        unfollow_link = unfollow_link + recipient
                    send_prr_email(  # Each subscriber needs to get a separate e-mail.
                        page=page,
                        recipients=[recipient],
                        subject=email_subject,
                        template=template,
                        include_unsubscribe_link=include_unsubscribe_link,
                        unfollow_link=unfollow_link,
                        notification_content=notification_content
                        )
        elif recipient_type == 'Staff participants':
            recipients = []
            participants = get_attribute(attribute='owners',
                    obj_id=request_id, obj_type='Request')
            for participant in participants:
                if participant.active:  # Only send an e-mail if they are active in the request
                    recipient = get_attribute(attribute='email',
                            obj_id=participant.user_id, obj_type='User')
                    if recipient:
                        recipients.append(recipient)
            send_prr_email(
                page=page,
                recipients=recipients,
                subject=email_subject,
                template=template,
                include_unsubscribe_link=include_unsubscribe_link,
                cc_everyone=False,
                unfollow_link=unfollow_link,
                notification_content=notification_content
                )
            app.logger.info('''

Recipients: %s''' % recipients)
        else:
            app.logger.info('Not a valid recipient type: %s'
                            % recipient_type)


def send_prr_email(
    page,
    recipients,
    subject,
    template,
    notification_content,
    request_id=None,
    include_unsubscribe_link=True,
    cc_everyone=False,
    password=None,
    unfollow_link=None,
    attached_file=None
    ):

    app.logger.info('''

Attempting to send an e-mail to %s with subject %s, referencing page %s and template %s'''
                    % (recipients, subject, page, template))
    if recipients:
        if send_emails:
            try:
                if "documents" in notification_content:
                    send_email(
                        body=render_template(
                            template,
                            unfollow_link=unfollow_link,
                            page=page,
                            request_id=request_id,
                            notification_content=notification_content
                            ),
                        recipients=recipients,
                        subject=subject,
                        include_unsubscribe_link=include_unsubscribe_link,
                        cc_everyone=cc_everyone,
                        attached_files=notification_content['documents'],
                        )
                    app.logger.info('''E-mail sent successfully!''')
                else:
                    send_email(
                        body=render_template(
                            template,
                            unfollow_link=unfollow_link,
                            page=page,
                            request_id=request_id,
                            notification_content=notification_content
                            ),
                        recipients=recipients,
                        subject=subject,
                        include_unsubscribe_link=include_unsubscribe_link,
                        cc_everyone=cc_everyone
                        )
                    app.logger.info('''E-mail sent successfully!''')
            except Exception, e:
                app.logger.info('''

There was an error sending the e-mail: %s'''
                                % e)
        else:
            app.logger.info('''

 E-mail flag turned off, no e-mails sent.''')


def send_email(
    body,
    recipients,
    subject,
    include_unsubscribe_link=True,
    cc_everyone=False,
    attached_files=None,
    ):

    mail = Mail(app)

    plaintext = ''
    html = body

    sender = app.config['DEFAULT_MAIL_SENDER']
    message = Message(sender=sender, subject=subject, html=html,
                      body=plaintext, bcc=sender)
    for file in attached_files:
        if file is not None:
            file.seek(0)
            # url = urllib.pathname2url(file)
            url = app.config['UPLOAD_FOLDER'] + "/" + file.filename
            content_type = mimetypes.guess_type(url)[0]
            filename = file.filename
            message.attach(filename=filename,
                           content_type=content_type, data=file.read())

    # if not include_unscubscribe_link:
    # message.add_filter('subscriptiontrack', 'enable', 0)

    if cc_everyone:
        pass
    else:

    # message.add_to(recipients[0])
    # for recipient in recipients:
    # ....if should_notify(recipeient):
    # ........message.add_cc(recipient)

        for recipient in recipients:
            recipient = recipient.replace('\\', '').replace("'", '')
            message.add_recipient(recipient)

    if send_emails:
        app.logger.info('''

 Attempting to send e-mail with body: %s, subject: %s, to %s'''
                        % (body, subject, recipients))
        try:
            mail.send(message)
            return True
        except Exception, e:
            app.logger.error('''

No e-mail was sent, error: %s'''
                             % e)
            return False
    app.logger.info("""

No e-mail was sent, probably because you're in a non-production environment.""")
    return False


def due_date(date_obj, extended=None, format=True):
    days_to_fulfill = 10
    if extended == True:
        days_to_fulfill = days_to_fulfill + 14
    if not date_obj:
        return None
    if type(date_obj) is not datetime:
        date_obj = datetime.strptime(date_obj, '%Y-%m-%dT%H:%M:%S.%f')
    due_date = date_obj + timedelta(days=days_to_fulfill)
    if format:
        return format_date(due_date)
    return due_date


def is_overdue(date_obj, extended=None):
    current_date = datetime.now()
    due = due_date(date_obj=date_obj, extended=extended, format=False)
    if current_date >= due:
        return (True, due)
    return (False, due)


def get_email_info(notification_type):
    email_json = open(os.path.join(app.root_path,
                      'static/json/emails.json'))
    json_data = json.load(email_json)
    return json_data['Notification types'][notification_type]


def notify_due():
    requests = get_objs('Request')
    email_json = open(os.path.join(app.root_path,
                      'static/json/emails.json'))
    json_data = json.load(email_json)
    for req in requests:
        status = req.solid_status
        if status != 'closed':

            # Check if it is due in 2 days

            if status == 'due soon':
                change_request_status(req.id, 'Due soon')
                email_subject = '%sPublic Records Request %s: %s' \
                    % (test, req.id, json_data['Notification types'
                       ]['Request due'])
            elif status == 'overdue':
                change_request_status(req.id, 'Overdue')
                email_subject = '%sPublic Records Request %s: %s' \
                    % (test, req.id, json_data['Notification types'
                       ]['Request overdue']['Subject'])
            else:
                continue
            recipients = get_staff_recipients(req)
            app_url = app.config['APPLICATION_URL']
            page = '%scity/request/%s' % (app_url, req.id)
            body = \
                "You can view the request and take any necessary action at the following webpage: <a href='%s'>%s</a>.</br></br> This is an automated message. You are receiving it because you are listed as the Public Records Request Liaison, Backup or Supervisor for your department." \
                % (page, page)

            # Need to figure out a way to pass in generic email template outside application context. For now, hardcoding the body.

            send_email(body=body, recipients=recipients,
                       subject=email_subject,
                       include_unsubscribe_link=False)


def get_staff_recipients(request):
    recipients = []
    owner_email = request.point_person().user.email
    if owner_email:
        recipients.append(owner_email)

    # Look up the department for the request, and get the contacts and backup:

    dept = request.department_name()
    if dept != 'N/A':
        contact_email = get_contact_by_dept(dept)
        if contact_email and contact_email not in recipients:
            recipients.append(contact_email)
        backup_email = get_backup_by_dept(dept)
        if backup_email and backup_email not in recipients:
            recipients.append(backup_email)
    if recipients:
        return recipients
    else:
        raise ValueError('No staff recipients for request %s'
                         % request.id)


def should_notify(user_email):
    """ Looks up the user in do_not_email.json and returns False if found. """

    do_not_email = open(os.path.join(app.root_path,
                        'static/json/do_not_email.json'))
    json_data = json.load(do_not_email)
    for department in json_data:
        emails = json_data[department]['Emails']
        for email in emails:
            if email.lower() == user_email.lower():
                return False
    return True


def format_date(obj):
    """ Take a datetime object and return it in format Jun 12, 2013 """

    if not obj:
        return None
    return helpers.localize(obj).strftime('%b %d, %Y')


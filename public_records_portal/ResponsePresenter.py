"""
    public_records_portal.RequestPresenter
    ~~~~~~~~~~~~~~~~

    Returns the html needed for the 'Response' portion of the case page.

"""

from flask.ext.login import current_user
from flask import flash, session
from flask.ext.session import Session
from secureCookie import *

import upload_helpers
import bleach

class ResponsePresenter:
    def __init__(self, record=None, note=None):
        if record:
            self.response = record
            self.update_url = "update_a_record_delete"
            if self.response.access:
                self.type = "offline"
            elif self.response.doc_id:
                self.type = "document"
            else:
                self.type = "link"
        if note:
            self.response = note
            if not (note.user_id) and int(note.privacy) == 2:
                self.response.text = "PRIVATE NOTE"
            self.update_url = "update_a_note_delete"
            self.type = "note"
            if "Request extended:" in self.response.text:
                self.type = "extension"
        if self.type == "offline":
            self.icon = "icon-file-alt icon-large"
        elif self.type == "note":
            self.icon = "icon-edit icon-large"
        elif self.type == "link":
            self.icon = "icon-link icon-large"
        elif self.type == "document":
            self.icon = "icon-file-alt icon-large"
        elif self.type == "extension":
            self.icon = "icon-calendar icon-large"

    def get_update_url(self):
        return self.update_url

    def get_id(self):
        return self.response.id

    def uid(self):
        return self.response.user_id

    def staff_name(self):
        return get_attribute(attribute="alias", obj_id=self.response.uid, obj_type="User")

    def staff_dept(self):
        return get_attribute(attribute="department", obj_id=self.response.uid, obj_type="User")

    def staff_phone(self):
        return get_attribute(attribute="phone", obj_id=self.response.uid, obj_type="User")

    def staff_email(self):
        return get_attribute(attribute="email", obj_id=self.response.uid, obj_type="User")

    def display_text(self):
        print current_user.is_anonymous
        if self.type == "offline":
            if current_user.role not in ['Agency Helpers'] and current_user.role is not None:
                if self.response.privacy:
                    return "Name of Record: %s<br> How to Access Record: %s <form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();'> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (bleach.clean(self.response.description), bleach.clean(self.response.access), session['_csrf_token'], self.response.request_id, self.response.id)
                else:
                    return "Name of Record: %s<br> How to Access Record: %s <form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();' checked> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (bleach.clean(self.response.description), bleach.clean(self.response.access), session['_csrf_token'], self.response.request_id, self.response.id)
            else:
                    if current_user.role in ['Agency Helpers'] or not(self.response.privacy):
                        return "Name of Record: %s<br> How to Access Record: %s" % (self.response.description, self.response.access)         
        elif self.type == "document":
            download_url = self.response.download_url
            if not download_url:
                download_url = upload_helpers.get_download_url(doc_id=self.response.doc_id, record_id=self.response.id)
                if not download_url:
                    download_url = "This document is still being uploaded, but it will be available shortly."
            return """
			<a href='%(download_url)s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%(download_url)s' target='_blank'><b>%(description)s </b></a>
			<a href = '%(download_url)s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='View document' target='_blank'><small><i class='icon-external-link'> </i></small></a>
			""" % {"download_url": download_url, "description": self.response.description, "url": self.response.url}
        elif self.type == "note":
            return self.response.text
        elif self.type == "link":
            if self.response.description and self.response.url and not(self.response.filename):
                if 'http' not in self.response.url:
                    self.response.url = 'http://' + self.response.url
                if current_user.role not in ['Agency Helpers'] and current_user.role is not None:    
                    if self.response.privacy: 
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();'> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (self.response.url, self.response.url, bleach.clean(self.response.description), session['_csrf_token'], self.response.request_id, self.response.id)
                    else:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();' checked> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (self.response.url, self.response.url, bleach.clean(self.response.description), session['_csrf_token'], self.response.request_id, self.response.id)
                else:
                        if current_user.role in ['Agency Helpers'] or not(self.response.privacy):
                            return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a>" % (self.response.url, self.response.url, self.response.description)      
            else:
                download_url = "/attachments/" + str(self.response.filename)
                if current_user.role not in ['Agency Helpers']  and current_user.role is not None:
                    if self.response.privacy:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();'> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (download_url, download_url, bleach.clean(self.response.description), session['_csrf_token'], self.response.request_id, self.response.id)
                    else:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='False' type='submit' onclick='action=this.form.submit();' checked> Public</input><input class='radio inline' type='radio' name='privacy_setting' value='True' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (download_url, download_url, bleach.clean(self.response.description), session['_csrf_token'], self.response.request_id, self.response.id)
                else:
                        if current_user.role in ['Agency Helpers'] or not(self.response.privacy):
                            return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a>" % (download_url, download_url, self.response.description)
        elif self.type == "extension":
            text = self.response.text.strip("Request extended:")
            return text

    def get_icon(self):
        return self.icon

    def set_icon(self, icon):
        self.icon = icon

    def date(self):
        return self.response.date_created

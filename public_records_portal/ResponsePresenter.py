"""
    public_records_portal.RequestPresenter
    ~~~~~~~~~~~~~~~~

    Returns the html needed for the 'Response' portion of the case page.

"""

import datetime

import bleach
from flask import session
from flask.ext.login import current_user

import upload_helpers
from models import RecordPrivacy
from public_records_portal import app


class ResponsePresenter:

    def __init__(self, record=None, note=None):
        if record:
            self.response = record
            self.update_url = "update_a_record_delete"
            if self.response.access:
                self.type = "offline"
            elif self.response.filename:
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
        app.logger.info("Type: %s\nPrivacy: %s\nID: %s\n" % (
            self.type, str(self.response.privacy), self.response.request_id))
        app.logger.info("Current User Anonymous: %s" %
                        current_user.is_anonymous)
        # app.logger.info("Release Date: %s\nCurrent Date: %s\nRelease Date < Current_Date: %s" % (str(self.response.release_date.strftime("%m%d%Y %H%M%S")), str(datetime.datetime.now().strftime("%m%d%Y %H%M%S")), str(self.response.release_date < datetime.datetime.now())))
        if self.type == "offline":
            if current_user.role not in ['Agency Helpers'] and current_user.role is not None:
                if self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC:
                    return "How to Access Record: <br />%s <form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();' checked> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (
                        bleach.clean(self.response.access), session[
                            '_csrf_token'], self.response.request_id,
                        self.response.id)
                elif self.response.privacy == RecordPrivacy.RELEASED_AND_PRIVATE:
                    return "How to Access Record: <br />%s <form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();' checked> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (
                        bleach.clean(self.response.access), session[
                            '_csrf_token'], self.response.request_id,
                        self.response.id)
                else:
                    return "How to Access Record: <br />%s <form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (
                        bleach.clean(self.response.access), session[
                            '_csrf_token'], self.response.request_id,
                        self.response.id)
            elif current_user.role in ['Agency Helpers']:
                return "How to Access Record: <br />%s" % self.response.access
            elif self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC and self.response.release_date and self.response.release_date < datetime.datetime.now():
                    return "How to Access Record: <br />%s" % (self.response.access)
            else:
                return None
        elif self.type == "document":
            if current_user.role not in ['Agency Helpers'] and current_user.role is not None:
                if self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC:
                    download_url = "/attachments/public/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();' checked> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (download_url, self.response.description, self.response.description, self.response.filename, session['_csrf_token'], self.response.request_id, self.response.id)
                elif self.response.privacy == RecordPrivacy.RELEASED_AND_PRIVATE:
                    download_url = "/attachments/private/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();' checked> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (download_url, self.response.description, self.response.description, self.response.filename, session['_csrf_token'], self.response.request_id, self.response.id)
                else:
                    download_url = "/attachments/private/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (download_url, self.response.description, self.response.description, self.response.filename, session['_csrf_token'], self.response.request_id, self.response.id)
            elif current_user.role in ['Agency Helpers']:
                if self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC:
                    download_url = "/attachments/public/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><br />" % (download_url, self.response.description, self.response.description, self.response.filename)
                elif self.response.privacy == RecordPrivacy.RELEASED_AND_PRIVATE:
                    download_url = "/attachments/private/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><br />" % (download_url, self.response.description, self.response.description, self.response.filename)
                else:
                    download_url = "/attachments/private/" + \
                        str(self.response.filename)
                    return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><br />" % (download_url, self.response.description, self.response.description, self.response.filename)
            elif (self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC) and (self.response.release_date is not None) and (self.response.release_date < datetime.datetime.now()):
                download_url = "/attachments/public/" + \
                    str(self.response.filename)
                return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s' target='_blank'><i class='icon-file'></i></i>&nbsp;<b>%s </b><br />%s </a><br />" % (download_url, self.response.description, self.response.description, self.response.filename)
            else:
                return None
        elif self.type == "note":
            response_text = self.response.text
            response_text = response_text.lstrip('{"')
            response_text = response_text.rstrip('"}')
            response_text = response_text.replace('","', " <br/><br/> ")
            return response_text
        elif self.type == "link":
            if self.response.description and self.response.url and not (self.response.filename):
                if 'http' not in self.response.url:
                    self.response.url = 'http://' + self.response.url
                if current_user.role not in ['Agency Helpers'] and current_user.role is not None:
                    if self.response.privacy == RecordPrivacy.RELEASED_AND_PUBLIC:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'><i class='icon-share'></i>&nbsp;<b>%s </b></a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();' checked> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (
                            bleach.clean(self.response.url), bleach.clean(
                                self.response.url),
                            bleach.clean(self.response.description), session[
                                '_csrf_token'], self.response.request_id,
                            self.response.id)
                    elif self.response.privacy == RecordPrivacy.RELEASED_AND_PRIVATE:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'><i class='icon-share'></i>&nbsp;<b>%s </b></a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();' checked> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();'> Private</input></form>" % (
                            bleach.clean(self.response.url), bleach.clean(
                                self.response.url),
                            bleach.clean(self.response.description), session[
                                '_csrf_token'], self.response.request_id,
                            self.response.id)
                    else:
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'><i class='icon-share'></i>&nbsp;<b>%s </b></a><form method='post' action='/switchRecordPrivacy'><input name=_csrf_token type=hidden value='%s'><input type='hidden' name='request_id' value='%s'/><input type='hidden' name='record_id' value='%s'/><input class='radio inline' type='radio' name='privacy_setting' value='release_and_public' type='submit' onclick='action=this.form.submit();'> Release and Public</input><input class='radio inline' type='radio' name='privacy_setting' value='release_and_private' type='submit' onclick='action=this.form.submit();'> Release and Private</input><input class='radio inline' type='radio' name='privacy_setting' value='private' type='submit' onclick='action=this.form.submit();' checked> Private</input></form>" % (
                            bleach.clean(self.response.url), bleach.clean(
                                self.response.url),
                            bleach.clean(self.response.description), session[
                                '_csrf_token'], self.response.request_id,
                            self.response.id)

                elif current_user.role in ['Agency Helpers'] or not (self.response.privacy):
                        return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'><i class='icon-share'></i>&nbsp;<b>%s </b></a>" % (
                            self.response.url, self.response.url, self.response.description)
                else:
                    return None

        elif self.type == "extension":
            text = self.response.text.strip("Request extended:")
            return text

    def get_icon(self):
        return self.icon

    def set_icon(self, icon):
        self.icon = icon

    def date(self):
        return self.response.date_created

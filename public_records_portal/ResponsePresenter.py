"""
    public_records_portal.RequestPresenter
    ~~~~~~~~~~~~~~~~

    Returns the html needed for the 'Response' portion of the case page.

"""



from models import Record, Note
import upload_helpers

class ResponsePresenter:
	def __init__(self, record = None, note = None):
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
			self.update_url = "update_a_note_delete"
			self.type = "note"
			if "Request extended:" in self.response.text:
				self.type = "extension"
		if self.type=="offline":
			self.icon = "icon-file-alt icon-large"
		elif self.type=="note":
			self.icon = "icon-edit icon-large"
		elif self.type=="link":
			self.icon = "icon-link icon-large"
		elif self.type =="document":
			self.icon = "icon-file-alt icon-large"
		elif self.type=="extension":
			self.icon = "icon-calendar icon-large"

	
	def get_update_url(self):
		return self.update_url

	def get_id(self):
		return self.response.id

	def uid(self):
		return self.response.user_id

	def staff_name(self):
		return get_attribute(attribute = "alias", obj_id = self.response.uid, obj_type = "User")

	def staff_dept(self):
		return get_attribute(attribute = "department", obj_id = self.response.uid, obj_type = "User")

	def staff_phone(self):
		return get_attribute(attribute = "phone", obj_id = self.response.uid, obj_type = "User")

	def staff_email(self):
		return get_attribute(attribute = "email", obj_id = self.response.uid, obj_type = "User")

	def display_text(self):
		if self.type == "offline":
			return "Name of Record: %s<br> How to Access Record: %s" %(self.response.description, self.response.access)
		elif self.type == "document":
			download_url = self.response.download_url
			if not download_url:
				download_url = upload_helpers.get_download_url(doc_id = self.response.doc_id, record_id = self.response.id)
				if not download_url:
					download_url = "This document is still being uploaded, but it will be available shortly."
			return """
			<a href='%(download_url)s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%(download_url)s' target='_blank'><b>%(description)s </b></a>
			<a href = '%(download_url)s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='View document' target='_blank'><small><i class='icon-external-link'> </i></small></a>
			""" %{"download_url": download_url, "description": self.response.description, "url": self.response.url} 
		elif self.type == "note":
			return self.response.text
		elif self.type == "link":
			#return "<a href='%s' rel='tooltip' data-toggle='tooltip' data-placement='top' data-original-title='%s'>%s </a>" % (self.response.url, self.response.url, self.response.description)
			download_url = "/attachments/" + str(self.response.filename)
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




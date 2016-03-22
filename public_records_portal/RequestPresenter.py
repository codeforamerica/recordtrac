"""
    public_records_portal.RequestPresenter
    ~~~~~~~~~~~~~~~~

    Returns the html needed for the 'Request' portion of the case page.

"""


from public_records_portal import models
from models import Note, QA
from db_helpers import get_obj
from flask.ext.babel import gettext as _

class RequestPresenter:
	def __init__(self, request, qa = None, note = None, index = None, public = False):
		self.index = index
		self.public = public
		self.request = request
		if qa:
			self.response = qa
			self.type = "qa"
			self.uid = self.response.owner_id
			self.staff = get_obj("User", self.uid)
			self.staff_email = _("N/A")
			self.staff_department = _("N/A")
			self.staff_phone = _("N/A")
			self.staff_alias = _("N/A")
			if self.staff:
				if self.staff.email:
					self.staff_email = self.staff.email
				if self.staff.department_id:
					self.staff_department = self.staff.department_id
				if self.staff.phone:
					self.staff_phone = self.staff.phone
				if self.staff.alias:
					self.staff_alias = self.staff.alias
			directory_popover = "directoryPopover('%s', '%s', '%s', '#contactinfoPopoverQA%s')" %(self.staff_email, self.staff_department, self.staff_phone, index)
			self.owner_link = '<a href="/staff_card/%s" data-placement="top" data-toggle="popover" href="#" id="contactinfoPopoverQA%s" class="hidden-phone hidden-tablet"><span class="contactinfoPopover" onmouseover="%s">%s</span></a>' % (self.response.owner_id, index, directory_popover, self.staff_alias or self.staff_email)
			self.icon = "icon-question icon-large"
		if note:
			self.response = note
			self.type = "note"
			self.icon = "icon-edit icon-large"

	def get_id(self):
		return self.response.id

	def display_text(self):
		if self.type == "qa":
			text = "%s - %s" %(self.response.question, self.owner_link)
			if self.response.answer:
				text = text + ("<p>%s - <span class='requester'>" + _("Requester") + "</span></p>") %(self.response.answer)
			else:
				if self.request.is_closed():
					text = text + "<i><p>" + _("No response from requester") + "</p></i>"
				else:
					if self.public:
						text = text + """
						<form name='respond_question' class='form-inline' id='answer' method='post' action='/update_a_qa' autocomplete='on'>
							<label class='control-label'>Answer</label><input type='hidden' name='qa_id' value='%s'/><input type='hidden' name='request_id' value='%s'/>
							<textarea id='answerTextarea' name='answer_text' class='input-xlarge' rows="2" type='text' rows='1' placeholder='""" + _("Can you respond to the above question?") + """' required/></textarea>
							<button id='askQuestion' class='btn btn-primary' type='submit'>""" + _("Respond") + """</button>
						</form>
						""" % (self.response.id, self.request.id)
					else:
						text = text + "<p>" + _("Requester hasn't answered yet.") + "</p>"
			return text
		elif self.type == "note":
			return ("%s - " + _("Requester")) %(self.response.text)

	def get_icon(self):
		return self.icon

	def set_icon(self, icon):
		self.icon = icon

	def date(self):
		return self.response.date_created

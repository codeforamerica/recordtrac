from public_records_portal import models
from models import Note, QA
from db_helpers import get_obj, get_owner_data
from helpers import *


class RequestTablePresenter:
	def __init__(self, request, public):
		self.request = request
		self.id = request.id
		if public:
			self.status = get_status(request, "public")
		else:
			status_arr = get_status(request = request, audience = "city", include_due_date = True)
			if status_arr:
				self.status, self.due_date = status_arr[0], date(status_arr[1])
			else:
				self.status, self.due_date = None, None
		if self.status == "open":
			self.color = "#2688AD"
		elif self.status == "closed":
			self.color = "#2a2b2b"
		elif self.status == "due soon":
			self.color = "#FB991B"
		else:
			self.color = "#CA1A1A"
		self.text = request.text
		if len(self.text) > 140:
			self.text = '%s...' % self.text[:140]
		self.status_icon = get_status_icon(self.status)
		self.department = get_dept_by_request(request)
		self.point_of_contact = get_owner_data(request.id, attributes = "alias")[0]
		if public:
			self.display_text = "<td class='status' bgcolor='%s'><small><i class='%s'></i></small>%s</td><td>%s</td><td>%s</td><td><div>%s</div></td><td>%s</td><td>%s</td><td style='display:none;'>%s</td>" %(self.color,self.status_icon,self.status,request.id, date(request.date_created), self.text, self.department, self.point_of_contact, request.text)
		else:
			self.display_text = "<td class='status' bgcolor='%s'><small><i class='%s'></i></small>%s</td><td>%s</td><td>%s</td><td><div>%s</div></td><td>%s</td><td>%s</td><td>%s</td><td style='display:none;'>%s</td>" %(self.color,self.status_icon,self.status,request.id, date(request.date_created), self.text, self.department, self.point_of_contact, (self.due_date or "N/A"), request.text)
			


from public_records_portal import models
from models import Note, QA
from db_helpers import get_obj, get_owner_data
from helpers import *
from filters import *


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
			self.color = "#2688AD;"
		if self.status == "closed":
			self.color = "#2a2b2b;"
		elif self.status == "due soon":
			self.color = "#FB991B;"
		else:
			self.color = "#CA1A1A;"

		self.status_icon = get_status_icon(self.status)
		self.department, self.point_of_contact = get_owner_data(request.id)
		if public:
			self.display_text = "<td bgcolor='%s'><small><i class='%s'></i></small>%s</td><td>%s</td><td>%s</td><td><div>%s</div></td><td>%s</td><td>%s</td><td>%s</td>" %(self.color,self.status_icon,self.status,request.id, date(request.date_created), request.text, self.department, self.point_of_contact, date_granular(request.status_updated))
		else:
			self.display_text = "<td bgcolor='%s'><small><i class='%s'></i></small>%s</td><td>%s</td><td>%s</td><td><div>%s</div></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" %(self.color,self.status_icon,self.status,request.id, date(request.date_created), request.text, self.department, self.point_of_contact, date_granular(request.status_updated), self.due_date)
			


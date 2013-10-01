from public_records_portal import models
from models import Note, QA
from db_helpers import get_obj, get_owner_data
from helpers import *
from filters import *


class RequestTablePresenter:
	def __init__(self, request, public):
		self.request = request
		self.due_date = None
		if public:
			self.status = get_status(request, "public")
		else:
			self.status, self.due_date = get_status(request = request, audience = "city", due_date = True)
		self.status_icon = get_status_icon(self.status)
		self.department, self.point_of_contact = get_owner_data(request.id)
		self.due_date = None
		self.display_text = "<td class='status %s'><small><i class='%s'></i></small>%s</td><td>%s</td><td>%s</td><td><div>%s</div></td><td>%s</td><td>%s</td><td>%s</td>" %(self.status,self.status_icon,self.status,request.id, date(request.date_created), request.text, self.department, self.point_of_contact, date_granular(request.status_updated))
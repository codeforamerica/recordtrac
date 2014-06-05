from public_records_portal import models, db
import csv


def export():
	city = True
	records = models.Request.query.all()
	# Need to write headers
	# outcsv.writerow([ column.name for column in models.Request.__mapper__.columns ])
	for curr in records:
		try:
			row = []
			for column in models.Request.__mapper__.columns:
				if column.name == 'current_owner':
					continue
				row.append(str(getattr(curr,column.name)))
			if city:
				row.append(str(curr.point_person_name()))
				row.append(str(curr.requester_name()))
			yield '%'.join(row) + '\n'
		except:
			pass

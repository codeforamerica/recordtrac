"""
    public_records_portal.csv_export
    ~~~~~~~~~~~~~~~~

    Implements an export to CSV function (for staff only) for relevant database fields.

"""

from public_records_portal import models


def export():
    records = models.Request.query.order_by(models.Request.id).all()
    db_headers = ['id', 'text', 'date_received', 'date_created', 'due_date', 'extended']
    all_headers = ['Request ID', 'Request Text', 'Date Received', 'Date Created', 'Date Due', 'Extended?',
                   'Requester First Name', 'Requester Last Name', 'Requester Phone', 'Agency Name',
                   'Point of Contact', 'All staff involved', 'Status']
    yield '\t'.join(all_headers) + '\n'
    for curr in records:
        row = []
        for name in db_headers:
            if name == 'text':
                text = getattr(curr, 'text')
                text = text.replace('\n', '').replace('\r', '').replace('\t', '')
                text = text.encode('utf8')
                row.append(str(text))
                continue
            row.append(str(getattr(curr, name)))
        requester_full_name = str(curr.requester_name()).split(" ")
        requester_first_name = requester_full_name[0]
        if requester_first_name != "N/A":
            requester_last_name = "".join(requester_full_name[1:])
        else:
            requester_last_name = "N/A"
        row.append(str(requester_first_name))
        row.append(str(requester_last_name))
        row.append(str(curr.requester_phone()))
        row.append(str(curr.department_name()))
        row.append(str(curr.point_person_name()))
        row.append(str(','.join(curr.all_owners())))
        row.append(str(curr.solid_status(cron_job=True)))
        yield '\t'.join(row) + '\n'

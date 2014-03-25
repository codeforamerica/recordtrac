import scribd
from public_records_portal import app, models
from timeout import timeout
from werkzeug import secure_filename
import tempfile
from db_helpers import *

# Set flags:
upload_to_scribd = False
if app.config['ENVIRONMENT'] != 'LOCAL':
    upload_to_scribd = True

# These are the extensions that can be uploaded to Scribd.com:
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff']


def progress(bytes_sent, bytes_total):
    app.logger.info("Scribd upload in progress: %s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(file, filename, API_KEY, API_SECRET, description):
    # Configure the Scribd API.
    scribd.config(API_KEY, API_SECRET)
    doc_id = None
    try:
        # Upload the document from a file.
        doc = scribd.api_user.upload(
            targetfile = file,
            name = filename,
            progress_callback=progress,
            req_buffer = tempfile.TemporaryFile()
            )  
        doc.description = description    
        doc.save() 
        doc_id = doc.id
        return doc_id
    except scribd.ResponseError, err:
        app.logger.info('Scribd failed: code=%d, error=%s' % (err.errno, err.strerror))
        return err.strerror

def get_scribd_download_url(doc_id, record_id = None, API_KEY = None, API_SECRET = None):
	if not API_KEY:
		API_KEY = app.config['SCRIBD_API_KEY']
	if not API_SECRET:
		API_SECRET = app.config['SCRIBD_API_SECRET']
	try:
		scribd.config(API_KEY, API_SECRET)
		doc = scribd.api_user.get(doc_id)
		doc_url = doc.get_download_url()
		if record_id:
			set_scribd_download_url(download_url = doc_url, record_id = record_id)
		return doc_url
	except:
		return None

def set_scribd_download_url(download_url, record_id):
    update_obj('download_url', download_url, obj_type = 'Record', obj_id = record_id)

def scribd_batch_download(): 
	req = Request.query.all()
	for record in req.records:
		if record.download_url:
			urllib.urlretrieve(record.downlaod_url, "saved_records/%s" %(record.filename))

def make_public(doc_id, API_KEY, API_SECRET):
    scribd.config(API_KEY, API_SECRET)
    doc = scribd.api_user.get(doc_id)
    doc.access = 'public'
    doc.save()

def make_private(doc_id, API_KEY, API_SECRET):
    scribd.config(API_KEY, API_SECRET)
    doc = scribd.api_user.get(doc_id)
    doc.access = 'private'
    doc.save()


def update_descriptions():
    scribd.config(app.config['SCRIBD_API_KEY'], app.config['SCRIBD_API_SECRET'])
    for doc in scribd.api_user.all():
        record = models.Record.query.filter_by(doc_id = doc.id).first()
        if record:
            link_back = app.config['APPLICATION_URL'] + 'request/' str(record.request_id)
            description =  "This document was uploaded via RecordTrac in response to a public records request for the %s. You can view the original request here: %s" % ( app.config['AGENCY_NAME'], link_back)
            doc.description = description
            doc.save()
            app.logger.info("\n\nUpdated Scribd document %s's description to %s" %(doc.id, description))



@timeout(seconds=20)
def upload_file(file, request_id): 
# Uploads file to scribd.com and returns doc ID. File can be accessed at scribd.com/doc/id
    if file:
        allowed = allowed_file(file.filename)
        if allowed[0]:
            filename = secure_filename(file.filename)
            if upload_to_scribd: # Check flag
                link_back = app.config['APPLICATION_URL'] + 'request/' + str(request_id)
                doc_id = upload(file = file, filename = filename, API_KEY = app.config['SCRIBD_API_KEY'], API_SECRET = app.config['SCRIBD_API_SECRET'], description = "This document was uploaded via RecordTrac in response to a public records request for the %s. You can view the original request here: %s" % (app.config['AGENCY_NAME'], link_back))
                return doc_id, filename
            else:
                return '1', filename # Don't need to do real uploads locally
        else:
            return allowed # Returns false and extension
    return None, None

### @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS, ext
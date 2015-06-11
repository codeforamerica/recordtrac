"""
    public_records_portal.scribd_helpers
    ~~~~~~~~~~~~~~~~

    Implements functions to interact with Scribd API for RecordTrac

"""


import os
import scribd
from public_records_portal import app, models
from timeout import timeout
from werkzeug import secure_filename
import tempfile


def should_upload():
    if app.config['ENVIRONMENT'] != 'LOCAL':
        return True
    elif 'UPLOAD_DOCS' in app.config:
        return True
    return False


# These are the extensions that can be uploaded to Scribd.com:
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf',
                      'sxw', 'sxc', 'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff']


def progress(bytes_sent, bytes_total):
    app.logger.info("Scribd upload in progress: %s of %s (%s%%)" %
                    (bytes_sent, bytes_total, bytes_sent*100/bytes_total))


def upload(document, filename, API_KEY, API_SECRET, description):
    app.logger.info("\n\nuploading file")
    # Configure the Scribd API.
    scribd.config(API_KEY, API_SECRET)
    doc_id = None
    try:
        # Upload the document from a file.
        doc = scribd.api_user.upload(
            targetfile=document,
            name=filename,
            progress_callback=progress,
            req_buffer=tempfile.TemporaryFile()
        )
        doc.description = description
        doc.save()
        doc_id = doc.id
        return doc_id
    except scribd.ResponseError, err:
        app.logger.info('Scribd failed: code=%d, error=%s' %
                        (err.errno, err.strerror))
        return err.strerror


def get_scribd_download_url(doc_id, record_id=None):
    if not should_upload():
        return None
        API_KEY = app.config['SCRIBD_API_KEY']
        API_SECRET = app.config['SCRIBD_API_SECRET']
        try:
            scribd.config(API_KEY, API_SECRET)
            doc = scribd.api_user.get(doc_id)
            doc_url = doc.get_download_url()
            if record_id:
                set_scribd_download_url(
                    download_url=doc_url, record_id=record_id)
            return doc_url
        except:
            return None


def set_scribd_download_url(download_url, record_id):
    update_obj(
        'download_url', download_url, obj_type='Record', obj_id=record_id)


def scribd_batch_download():
    req = Request.query.all()
    for record in req.records:
        if record.download_url:
            urllib.urlretrieve(
                record.downlaod_url, "saved_records/%s" % (record.filename))


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


def update_descriptions(API_KEY, API_SECRET):
    scribd.config(API_KEY, API_SECRET)
    for doc in scribd.api_user.all():
        record = models.Record.query.filter_by(doc_id=doc.id).first()
        if record:
            link_back = app.config['APPLICATION_URL'] + \
                'request/' + str(record.request_id)
            description = "This document was uploaded via RecordTrac in response to a public records request for the %s. You can view the original request here: %s" % (
                app.config['AGENCY_NAME'], link_back)
            doc.description = description
            doc.save()
            app.logger.info(
                "\n\nUpdated Scribd document %s's description to %s" % (doc.id, description))


#@timeout(seconds=20)
def upload_file(document, request_id):
    # Uploads file to scribd.com and returns doc ID. File can be accessed at
    # scribd.com/doc/id
    app.logger.info("\n\nscribd upload file")
    if not should_upload():
        app.logger.info("\n\nshoud not upload file")
        return '1', None  # Don't need to do real uploads locally
    if document:
        app.logger.info("\n\nbegin file upload")
        allowed = allowed_file(document.filename)
        app.logger.info("\n\n%s is allowed: %s" %
                        (document.filename, allowed[0]))
        if allowed[0]:
            filename = secure_filename(document.filename)
            app.logger.info(
                "\n\nfilename after secure_filename: %s" % (filename))
            link_back = app.config[
                'APPLICATION_URL'] + 'request/' + str(request_id)
            app.logger.info("\n\nlink_back: %s" % (link_back))
            #doc_id = upload(document = document, filename = filename, API_KEY = app.config['SCRIBD_API_KEY'], API_SECRET = app.config['SCRIBD_API_SECRET'], description = "This document was uploaded via RecordTrac in response to a public records request for the %s. You can view the original request here: %s" % (app.config['AGENCY_NAME'], link_back))
            # return doc_id, filename

            upload_path = upload_file_locally(document, filename, request_id)
            return upload_path, filename

        else:
            return allowed  # Returns false and extension
    return None, None


def upload_file_locally(document, filename, request_id):
    app.logger.info("\n\nuploading file locally")
    app.logger.info("\n\n%s" % (document))

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    app.logger.info("\n\nupload path: %s" % (upload_path))

    document.save(upload_path)
    app.logger.info("\n\nfile uploaded to local successfully")

    return upload_path


# @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS, ext

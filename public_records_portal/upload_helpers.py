"""
    public_records_portal.upload_helpers
    ~~~~~~~~~~~~~~~~

    Implements functions to upload files

"""

import os

from werkzeug import secure_filename
import pyclamd

from public_records_portal import app


def should_upload():
    if app.config['ENVIRONMENT'] != 'LOCAL':
        return True
    elif 'UPLOAD_DOCS' in app.config:
        return True
    return False

# These are the extensions that can be uploaded:
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'ps', 'rtf', 'epub', 'key', 'odt', 'odp', 'ods', 'odg', 'odf', 'sxw', 'sxc',
                      'sxi', 'sxd', 'ppt', 'pps', 'xls', 'zip', 'docx', 'pptx', 'ppsx', 'xlsx', 'tif', 'tiff']
clamdiagnostic = pyclamd.ClamdAgnostic()


def get_download_url(doc_id, record_id=None):
    if not should_upload():
        return None


# @timeout(seconds=20)
def upload_file(document, request_id):
    # Uploads file to local directory, returns upload_path, filename
    app.logger.info("\n\nLocal upload file")
    if not should_upload():
        app.logger.info("\n\nshoud not upload file")
        return '1', None  # Don't need to do real uploads locally
    if document:
        app.logger.info("\n\nbegin file upload")
        allowed = allowed_file(document.filename)
        app.logger.info("\n\n%s is allowed: %s" % (document.filename, allowed[0]))
        if allowed[0]:
            filename = secure_filename(document.filename)
            app.logger.info("\n\nfilename after secure_filename: %s" % (filename))
            link_back = app.config['APPLICATION_URL'] + 'request/' + str(request_id)
            app.logger.info("\n\nlink_back: %s" % (link_back));

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

    if clamdiagnostic.scan_file(upload_path) is not None:
        os.remove(upload_path)
        app.logger.info("\n\nVirus found in uploaded file, file deleted")
        return "VIRUS_FOUND"

    app.logger.info("\n\nfile uploaded to local successfully")

    return upload_path


### @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS, ext

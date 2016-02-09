"""
    public_records_portal.upload_helpers
    ~~~~~~~~~~~~~~~~

    Implements functions to upload files

"""

import datetime
import os
import subprocess
import socket
import sys
import traceback

from werkzeug.utils import secure_filename

from public_records_portal import app


def should_upload():
    if app.config['ENVIRONMENT'] != 'LOCAL':
        return True
    elif 'UPLOAD_DOCS' in app.config:
        return True
    return False


# These are the extensions that can be uploaded:
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'rtf', 'odt', 'odp', 'ods', 'odg', 'odf',
                      'ppt', 'pps', 'xls', 'docx', 'pptx', 'ppsx', 'xlsx',
                      'jpg','jpeg','png','gif','tif','tiff','bmp',
                      'avi','flv','wmv','mov','mp4',
                      'mp3','wma','wav','ra','mid']
                      
HOST="127.0.0.1"
SERVICE = app.config['SERVICE']
PORT = int(app.config['PORT'])


def get_download_url(doc_id, record_id=None):
    if not should_upload():
        return None

def upload_multiple_files(documents, request_id):
    for document in documents:
        upload_file(document=document, request_id=request_id)

# @timeout(seconds=20)
def upload_file(document, request_id, privacy = True):
    """
    Takes an uploaded file, scans it using an ICAP Scanner, and stores the
    file if the scan passed
    :param document: File
    :param request_id: Current request identifier
    :return:
    """
    if not should_upload():
        app.logger.info("Upload functionality has been disabled")
        return '1', None, None

    if app.config['SHOULD_SCAN_FILES'] == 'True':
        file_length = document.read()
        document.seek(0)
        if file_length < 0:
            app.logger.error("File: %s is too small" % document.filename)
            return None, None, None
        if file_length > app.config['MAX_FILE_SIZE']:
            app.logger.error("File: %s is too large" % document.filename)
            return None, None, None
        if allowed_file(document.filename):
            file_scanned = scan_file(document)

def scan_file(document):
    socket = connect_to_icap_server()
    if not socket:
        return None

    icap_request = "RESPMOD icap://%s:%s/%s%s ICAP/1.0\r\n" % (app.config['ICAP_SERVER'], app.config['ICAP_PORT'], app.config['ICAP_SERVICE_NAME'], app.config['ICAP_PROFILE']
    icap_request += "Allow: 204\r\n"
    icap_request += "Encapsulated: req-hdr=%s res-hdr=%s res-body=%s\r\n" % ()


def connect_to_icap_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        app.logger.error("Error binding socket\n%s\n" % msg[1])
        return None

    try:
        sock.connect((app.config['ICAP_SERVER'], app.config['ICAP_PORT']))
    except socket.error, msg:
        app.logger.error("Error connecting to %s:%s\n%s" % (app.config['ICAP_SERVER'], app.config['ICAP_PORT'], msg[1]))
        return None
    return sock

def upload_file_locally(document, filename, privacy):
    app.logger.info("\n\nuploading file locally")
    app.logger.info("\n\n%s" % (document))


    if privacy == u'True':
        upload_path = os.path.join(app.config['UPLOAD_PRIVATE_LOCAL_FOLDER'], filename)
    elif privacy == u'False':
        upload_path = os.path.join(app.config['UPLOAD_PUBLIC_LOCAL_FOLDER'], filename)
    app.logger.info("\n\nupload path: %s" % (upload_path))

    document.save(upload_path)

    app.logger.info("\n\nfile uploaded to local successfully")

    return upload_path


### @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS
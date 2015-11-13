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
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'rtf','odt', 'odp', 'ods', 'odg', 'odf',
                     'ppt', 'pps', 'xls', 'docx', 'pptx', 'ppsx', 'xlsx']
HOST=app.config['HOST']
SERVICE=app.config['SERVICE']
PORT=app.config['PORT']

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
    if allowed_file(document.filename):
        app.logger.info("\n\nbegin file upload")
        # REQMOD, POST
        print "----- REQMOD - POST -----"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print "Unable to bind socket and create connection to ICAP server."

        try:
            sock.connect((HOST, PORT))
        except socket.error, msg:
            print("[ERROR] %s\n" % msg[1])
            print("Unable to verify file for malware. Please try again.")

        sock.send( "REQMOD %s ICAP/1.0\r\n" % ( SERVICE ) )
        sock.send( "Host: %s\r\n" % ( HOST ) )
        sock.send( "Encapsulated: req-hdr=0, null-body=170\r\n" )
        sock.send( "\r\n" )

        sock.send( "POST / HTTP/1.1\r\n" )
        sock.send( "Host: www.origin-server.com\r\n" )
        sock.send( "Accept: text/html, text/plain\r\n" )
        sock.send( "Accept-Encoding: compress\r\n" )
        sock.send( "Cookie: ff39fk3jur@4ii0e02i\r\n" )
        sock.send( "If-None-Match: \"xyzzy\", \"r2d2xxxe\"\r\n" )
        sock.send( "\r\n" )
        with open(document, "rb") as uploadedFile:
          f = uploadedFile.read()
          b = bytearray(f)
        sock.send( uploadedFile )
        sock.send( "OPTIONS icap://"+app.config(['HOST'])+":"+app.config(['PORT'])+"/wwrespmod?profile=default ICAP/1.0" )
        sock.send( "Host: %s\r\n" % ( HOST ) )
        sock.send( "ICAP/1.0 200 OK" )
        sock.send( "Methods: REQMOD, RESPMOD")
        sock.send( "Options-TTL: 3600")
        sock.send( "Encapsulated: null-body=0")
        sock.send( "Max-Connections: 400")
        sock.send( "Preview: 30")
        sock.send( "Service: McAfee Web Gateway 7.5.2 build 20202")
        sock.send( '''ISTag: "00004154-2.26.156-00007980"''')
        sock.send( "Allow: 204")

        data = sock.recv(2048)
        string = data
        if "200 OK" in string:
            app.logger.info("\n\n%s is allowed: %s" % (document.filename, allowed[0]))
            filename = secure_filename(document.filename)
            upload_path = upload_file_locally(document, filename, request_id)
            return upload_path, filename
        else:
            # Loop not completed
            app.logger.error("Malware detected. Loop user around.")
            return None, None
    return None, None


def upload_file_locally(document, filename, request_id):
    app.logger.info("\n\nuploading file locally")
    app.logger.info("\n\n%s" % (document))

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    app.logger.info("\n\nupload path: %s" % (upload_path))

    document.save(upload_path)

    # if clamdiagnostic.scan_file(upload_path) is not None:
    #     os.remove(upload_path)
    #     app.logger.info("\n\nVirus found in uploaded file, file deleted")
    #     return "VIRUS_FOUND"

    app.logger.info("\n\nfile uploaded to local successfully")

    return upload_path


### @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS

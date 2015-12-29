"""
    public_records_portal.upload_helpers
    ~~~~~~~~~~~~~~~~

    Implements functions to upload files

"""

import datetime
import os
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
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'doc', 'rtf', 'odt', 'odp', 'ods', 'odg',
                      'odf',
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


# @timeout(seconds=20)
def upload_file(document, request_id):
    """
    Takes an uploaded file, scans it using an ICAP Scanner, and stores the
    file if the scan passed
    :param document: File
    :type document:
    :param request_id: Current request
    :type request_id:
    :return:
    :rtype:
    """
    app.logger.info("\n\nLocal upload file")
    if not should_upload():
        app.logger.info("\n\nshoud not upload file")
        return '1', None, None  # Don't need to do real uploads locally
    if app.config["SHOULD_SCAN_FILES"]:
        if allowed_file(document.filename) and len(document.read()) > 10000000:
            app.logger.error("Error with filesize.")
            error = "Error with the file size. Check to make sure it is less than 10 MB."
            return None, None, error
        if allowed_file(document.filename):
            app.logger.info("\n\nbegin file upload")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error, msg:
                app.logger.error("Unable to bind socket and create connection to ICAP server.")

            try:
                sock.connect((SERVICE, PORT))
            except socket.error, msg:
                app.logger.error("[ERROR] %s\n" % msg[1])
                app.logger.error("Unable to verify file for malware. Please try again.")
            app.logger.info("----- RESPMOD -----")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error, msg:
                sys.stderr.write("[ERROR] %s\n" % msg[1])
                app.logger.error("Error at socket.")
            try:
                sock.connect((SERVICE, PORT))
            except socket.error, msg:
                sys.stderr.write("[ERROR] %s\n" % msg[1])
                app.logger.error("Error at socket.")
            today = datetime.date.today()
            cDate = today.strftime("%a, %d %b %Y")
            time = datetime.datetime.now()
            cTime = time.strftime("%H:%M:%S")
            sock.send( "RESPMOD %s ICAP/1.0\r\n" % ( SERVICE ) )
            sock.send( "Host: %s\r\n" % ( HOST ) )
            sock.send( "Encapsulated: req-hdr=0, res-hdr=137, res-body=296\r\n" )
            sock.send( "\r\n" )
            sock.send( "GET /origin-resource HTTP/1.1\r\n" )
            sock.send( "Host: www.origin-server.com\r\n" )
            sock.send( "Accept: text/html, text/plain, image/gif, application/pdf, application/msword, application/rtf, application/vnd.oasis.opendocument.text, application/vnd.oasis.opendocument.presentation, application/vnd.oasis.opendocument.spreadsheet, application/vnd.oasis.opendocument.graphics, application/vnd.oasis.opendocument.formula, application/vnd.ms-powerpoint, application/vnd.ms-powerpoint.slideshow.macroenabled.12, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.openxmlformats-officedocument.presentationml.presentation, application/vnd.openxmlformats-officedocument.presentationml.slideshow, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, image/jpeg, image/png, image/tiff, image/bmp, video/x-msvideo, video/x-flv, video/x-ms-wmv, video/quicktime, video/mp4, audio/mpeg, audio/x-ms-wma, audio/x-wav, audio/x-pn-realaudio, audio/midi\r\n" )
            sock.send( "Accept-Encoding: gzip, compress\r\n" )
            sock.send( "\r\n" )
            sock.send( "HTTP/1.1 200 OK\r\n" )
            sock.send( "Date: "+cDate +" "+cTime+" GMT\r\n" )
            sock.send( "Server: Apache/1.3.6 (Unix)\r\n" )
            sock.send( 'ETag: "63840-1ab7-378d415b"\r\n' )
            sock.send( "Content-Type: text/html\r\n" )
            sock.send( "Content-Length: "+ str(len(document.read()))+"\r\n" )
            document.seek(0)
            sock.send( "\r\n" )
            sock.send( "33\r\n" )
            sock.send(document.read()+"\r\n")
            sock.send( "0\r\n" )
            sock.send( "\r\n" )
            document.seek(0)
            try:
                data = sock.recv(1024)
                string = data
                app.logger.info(data)
            except:
                app.logger.error(traceback.format_exc())
            if "200 OK" in string:
                app.logger.info("\n\n%s is allowed: %s" % (document.filename, string))
                filename = secure_filename(document.filename)
                upload_path = upload_file_locally(document, filename, request_id)
                return upload_path, filename, None
            else:
                app.logger.error("Malware detected. Upload failed")
                sock.close()
                return None, None, None
        return None, None, None
    sock.close()
    return "1", None, None


def upload_file_locally(document, filename, request_id):
    app.logger.info("\n\nuploading file locally")
    app.logger.info("\n\n%s" % (document))

    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    app.logger.info("\n\nupload path: %s" % (upload_path))

    document.save(upload_path)

    app.logger.info("\n\nfile uploaded to local successfully")

    return upload_path


### @export "allowed_file"
def allowed_file(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext in ALLOWED_EXTENSIONS

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
        file_length = len(document.read())
        document.seek(0)
        app.logger.info("File Size: %s\nMAX_FILE_SIZE: %s\n" % (file_length, app.config['MAX_FILE_SIZE']))
        if file_length < 0:
            app.logger.error("File: %s is too small" % document.filename)
            return None, None, "file_too_small"
        if file_length > app.config['MAX_FILE_SIZE']:
            app.logger.error("File: %s is too large" % document.filename)
            return None, None, "file_too_large"
        if allowed_file(document.filename):
            file_scanned = scan_file(document, file_length)
            if file_scanned == 0:
                upload_file_locally(document, document.filename, privacy)
                return 1, secure_filename(document.filename), None
            else:
                return None, None, None
        else:
            return None
    else:
        upload_file_locally(document, document.filename, privacy)
        return 1, secure_filename(document.filename), None

def scan_file(document, file_length):
    current_file_location = 0
    server_response = ""
    return_value, sock = connect_to_icap_server()
    while return_value == 0:
        request_header = "GET http://%s/%s/%s HTTP/1/1\r\n" % (socket.gethostbyname(socket.gethostname()), datetime.datetime.now().strftime("%Y%m%d%H%M%S"), document.filename.split(".")[-1])
        request_header = "Host: %s\r\n\r\n"

        response_header = "HTTP/1.1 200 OK \r\n"
        response_header += "Transfer-Encoding: chunked\r\n\r\n"

        icap_request = "RESPMOD icap://%s:%s/%s%s ICAP/1.0\r\n" % (app.config['ICAP_SERVER'], app.config['ICAP_PORT'], app.config['ICAP_SERVICE_NAME'], app.config['ICAP_PROFILE'])
        icap_request += "Allow: 204\r\n"
        icap_request += "Encapsulated: req-hdr=%s res-hdr=%s res-body=%s\r\n" % (0, len(response_header), (len(request_header) + len(response_header)))
        icap_request += "Host: %s\r\n" % (app.config['ICAP_SERVER'])
        icap_request += "Preview: %s\r\n" % (str(30))
        icap_request += "User-Agent: PythonIcapClient\r\n"
        icap_request += "X-Client-IP: %s\r\n\r\n" % (socket.gethostbyname(socket.gethostname()))

        send = send_to_icap(icap_request, sock)
        if send == -1:
            break

        send = send_to_icap(request_header, sock)
        if send == -1:
            break

        send = send_to_icap(response_header, sock)
        if send == -1:
            break

        file_to_scan = bytearray(document.read())
        icap_request = "";
        try:
            icap_request += "%s\r\n" % str(30)
            send = send_to_icap(icap_request, sock)
            if send == -1:
                break

            icap_request = "\r\n0\r\n\r\n"
            string = file_to_scan[current_file_location:current_file_location+30]
            send = send_to_icap(string, sock)
            if send == -1:
                break
            current_file_location += 30
            send = send_to_icap(icap_request, sock)
            if send == -1:
                break
        except Exception, e:
            app.logger.error("Failed to send preview: %s\n" % e)
            return_value = -1

        icap_request = ""
        data = sock.recv(4096)
        if "ICAP/1.0 100" not in data:
            server_response = data
            disconnect(sock)
            break
        else:
            file_length = file_length - 30
            icap_request += "%s\r\n" % file_length
            send = send_to_icap(icap_request, sock)
            if send == -1:
                break
            string = file_to_scan[30:]
            string += "\r\n0\r\n"
            send = send_to_icap(string, sock)
            if send == -1:
                break
            data = sock.recv(4096)
            server_response = check_icap_response(data)
            if server_response == -1:
                break
            disconnect(sock)
            break
    return server_response


def send_to_icap(string, sock):
    return_value = 0
    counter = 0
    try:
        sock.send(string + "\n")
        counter += 1
    except socket.error, msg:
        app.logger.error("Failed to write send file to ICAP Server: %s\n\n" % (string, msg[1]))
        return_value = -1
    return return_value


def connect_to_icap_server(server=app.config['ICAP_SERVER'], port=app.config['ICAP_PORT']):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        app.logger.error("Error binding socket\n%s\n" % msg[1])
        return (-1, None)

    try:
        sock.connect((server, int(port)))
    except socket.error, msg:
        app.logger.error("Error connecting to %s:%s\n%s" % (server, port, msg[1]))
        return (-1, None)
    return (0, sock)


def check_icap_response(response):
    return_value = ""
    status = "Undefined"
    block_result = ""
    virus_name = ";"

    lines = response.split("\n")

    for line in lines:
        if line.startswith("ICAP/1.0 204"):
            status = "Clean:"
            block_result = 0
            virus_name = "No malware detected;"
            break
        if line.startswith("ICAP/1.0 200"):
            status = "Blocked"
            block_result = "200"
            continue
        if line.startswith("X-Virus-Name:"):
            status = "Infected:"
            if line[:14].startswith(virus_name):
                virus_name = line[:14]
            else:
                virus_name += line[:14]
            virus_name += ";"
            continue
        if line.startswith("X-WWBlockResult:"):
            block_result = int(line[17])
            if block_result == 90:
                virus_name += "Policy:Unwanted Unsigned Content;"
            if block_result == 81:
                virus_name += "Policy:Authorization needed;"
            if block_result == 45:
                virus_name += "Policy:Macros unwanted;"
            if block_result == 44:
                virus_name += "Policy:Office document unreadable;"
            if block_result == 43:
                virus_name += "Policy:Encrypted document unwanted;"
            if block_result == 42:
                virus_name += "Policy:ActiveX unwanted;"
            if block_result == 41:
                virus_name == "Policy:Document Inspector;"
            if block_result == 40:
                virus_name == "Policy:Text Categorization unwanted;"
            if block_result == 34:
                virus_name += "Policy:Encrypted archive unwanted;"
            if block_result == 33:
                virus_name += "Policy:Archive recursion level exceeded"
            if block_result == 32:
                virus_name += "Policy:Mailbomb unwanted;"
            if block_result == 31:
                virus_name += "Policy:Corrupted archive unwanted;"
            if block_result == 30:
                virus_name += "Policy:Multipart archive unwanted;"
            if block_result == 23:
                virus_name += "Policy:Generic Body Filter;"
            if block_result == 22:
                virus_name += "Policy:Media type blacklisted;"
            if block_result == 21:
                virus_name += "Policy:Media type mismatch;"
            else:
                status = "Infected:"
            continue

        if line.startswith("ICAP/1.0 "):
            status = "Error: %s" % line
    if virus_name.endswith(";"):
        virus_name = virus_name[:-1]
    if virus_name == "":
        virus_name = "Unknown"
    if status != "Clean:":
        app.logger.error("%s%s:\"%s\"\n" % (status, block_result, virus_name))
        return -1
    return 0

def disconnect(sock):
    try:
        sock.close()
    except socket.error, msg:
        app.logger.error("Failed to close socket\n%s\n" % msg[1])
        return -1


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
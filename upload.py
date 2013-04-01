"""
Uploading a text file to scribd.com.
"""

import time
import logging
import tempfile
import scribd


# Set your API key and secret here.
API_KEY = '4ure8weqmh0ert8t7ntht'
API_SECRET = 'sec-bu2du9d37n6dngvt77h6rybvzn'


last_bytes_sent = 0
def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(filepath):
    # Configure the Scribd API.
    scribd.config(API_KEY, API_SECRET)
    doc_id = None
    try:
        # Upload the document from a file.
        doc = scribd.api_user.upload(
            open(filepath,'rb'),
            progress_callback=progress,
            req_buffer = tempfile.TemporaryFile()
            )
        # Poll API until conversion is complete.
        while doc.get_conversion_status() != 'DONE':
            # Sleep to prevent a runaway loop that will block the script.
            time.sleep(2)        
        doc_id = doc.id
    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)
    return doc_id

if __name__ == '__main__':
    main()

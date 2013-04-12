"""
Uploading a text file to scribd.com.
"""

import time
import logging
import tempfile
import scribd




last_bytes_sent = 0
def progress(bytes_sent, bytes_total):
    print("%s of %s (%s%%)" % (bytes_sent, bytes_total, bytes_sent*100/bytes_total))

def upload(filepath, API_KEY, API_SECRET):
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
        return doc_id
    except scribd.ResponseError, err:
        print 'Scribd failed: code=%d, error=%s' % (err.errno, err.strerror)
        return err.strerror

if __name__ == '__main__':
    main()

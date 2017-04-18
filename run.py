from public_records_portal.prflask import app
from os.path import isdir

if isdir('.certs'):
    app.run(debug=True, port=8080, ssl_context=('.certs/openrecords.crt', '.certs/openrecords.key'))
else:
    app.run(debug=True, port=8080, ssl_context='adhoc')

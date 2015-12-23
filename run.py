from public_records_portal.prflask import app
from OpenSSL import SSL
app.run(debug=True, port=5000)

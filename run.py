from public_records_portal.prflask import app
from OpenSSL import SSL
#context = SSL.Context(SSL.SSLv23_METHOD)
#app.run(debug=True, port=5000)
context = ('/Users/administrator/recordtrac-master-20151215/server.crt','/Users/administrator/recordtrac-master-20151215/server.key')
#app.run(debug=True, port=5000, ssl_context=context)
#app.run(debug=True, port=5000)
#app.run(host='10.211.55.2', debug=True, port=5000)
app.run(host='10.211.55.2', debug=True, port=5000, ssl_context=context)
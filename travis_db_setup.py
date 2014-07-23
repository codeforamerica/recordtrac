from public_records_portal import models, prr
models.db.drop_all()
models.db.create_all()

# Create some seed data so our tests run
request = models.Request(text = "Hi, this is a request")
models.db.session.add(request)
models.db.session.commit()
user = models.User(email = "richa@example.org", password = "a password")
owner = models.Owner(request_id = request.id, reason = "A reason", user_id = user.id)
models.db.session.add(owner)
models.db.session.commit()

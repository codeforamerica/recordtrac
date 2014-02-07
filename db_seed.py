from public_records_portal import prr, db_helpers, departments
from public_records_portal.prflask import app
import os, random, string, json

# Set directory fields from information in the directory.json file
prr.set_directory_fields()

# Update user info with information in the departments.json file
departments.populate_users_with_departments()

common_requests = ['City Council meeting minutes', 'Police Report', 'Incident Report', 'Communication between Councilmembers']
depts_json = open(os.path.join(app.root_path, 'static/json/list_of_departments.json'))
staff_json = open(os.path.join(app.root_path, 'static/json/staff_emails.json'))
departments = json.load(depts_json)
people = json.load(staff_json)
reasons = ['They have the document', 'They would know more about this', 'They are my backup', 'Can you look into this?']
documents = ['Minutes', 'Report']
answers = ["Yep, thanks so much!", "No, nevermind then."]

# Create some seed data so our tests run
for i in range(20):
	request_type = random.choice(common_requests)
	request_department = random.choice(departments)
	random_number = random.randrange(0, 901, 4)
	another_random_number =  random.randrange(0, 901, 4)
	request_text = "%(request_type)s %(random_number)s" % locals()
	request_id, success = prr.make_request(text=request_text, department = request_department)
	if success:
		prr.add_note(request_id = request_id, text = "We're working on this and will get back to you shortly.", user_id = 2)
		qa_id = prr.ask_a_question(request_id = request_id, owner_id = 1, question = "You specified %(random_number)s, but that does not exist. Did you mean %(another_random_number)s? " % locals())
		if qa_id:
			answer = random.choice(answers)
			prr.answer_a_question(qa_id = qa_id, answer = answer)
			if "Yep" in answer:
				prr.add_link(request_id = request_id, url = "http://www.postcode.io", description = "Report %(another_random_number)s" % locals(), user_id = 3)
			else:
				prr.close_request(request_id = request_id, reason = "Record does not exist.", user_id = 4)
		prr.assign_owner(request_id = request_id, reason = random.choice(reasons), email = random.choice(people))
		db_helpers.add_staff_participant(request_id = request_id, email = random.choice(people), reason = random.choice(reasons))
		


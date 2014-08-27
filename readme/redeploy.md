#How to create a new RecordTrac app for your agency 


## Groundwork
To redeploy RecordTrac, you need support from key stakeholders _within_ government. The administrator or elected official in charge of overseeing public records request must agree to use this system, and instruct their colleagues to do so. 

RecordTrac assumes there is a contact for a given municipality or department within the municipality to handle public records requests. If a government agency has no process at all in place, but is interested in using the system, they could start with one ‘champion’ that is knowledgeable about who has access to different records. The champion can then route requests to the proper parties within government who may have the documents or information a requester needs. 

## Best Practices
RecordTrac is flexible and could complement almost any governmental agency's process for fulfilling records requests. There are however, best practices a governmental agency should adopt to really leverage the power of RecordTrac. Here is a good starting set:

* Track all public records requests through RecordTrac, even if you originally received it over the phone, by email, fax, or mail. 

* Don't reveal sensitive information in your message or upload documents that haven't been thoroughly redacted. Everything you do on the site is immediately viewable to the public.

* Upload scanned copies of the [redacted] records to RecordTrac. This prevents you from answering the same public records request multiple times. It provides proof you responded to the request.

* Communicate with everyone through RecordTrac. (Only take conversations offline if it involves confidential or sensitive information.) 

* Make your messages or the documents you upload understood by everyone--not just the requester. You can do this by doing the following:
	* Explain all acronyms used.
	* Give each uploaded document a unique name.  
	* If you have to enter a request on behalf of a member of the public, describe the request and/or include a copy of it in your response.  

* Review requests no later than two business days after you receive them.

## Redeploy
RecordTrac is an open source project, and we'd love for you to use it yourself!

**EDIT**  Following this documentation, a semi-technical user — someone with experience using a terminal or command prompt — who has an idea of what kind of survey they would like to run should be able to get CityVoice up and running in a relatively short amount of time (less than a day).  **EDIT** 

Using the recommended deployment instructions below, the technical operating costs (hosting and other services) should total about $100 per month.  

If you have problems using RecordTrac, please [open an issue on GitHub](https://github.com/codeforamerica/recordtrac/issues) and let us know what problems or difficulties you encountered in as much detail as you can.

### Initial Setup

**THERE ARE SOME INTERIM STEPS BEFORE CREATING A DATABASE** (Heroku install, create Heroku app, clone RecordTrac database, push to Heroku)

### Deploy RecordTrac on Heroku

#### Create a database
* Use Heroku's add-ons to set up a 'Heroku Postgres' database. 
* Access the Heroku command line by running `heroku run bash`, and create the database tables by running `python db_setup.py`. 

Technically, that is all you need to get an instance of RecordTrac running with the supplied defaults. But to get a minimum *production-ready* environment running, here's the information you'll need to provide:

#### Set environment variables

* **Agency name**: 
Set `AGENCY_NAME` to the name of your agency, which is used across the site (ex. "City of Oakland").

* **Agency logos**: 
`LOGO_ON_WHITE_URL`, `LOGO_ON_BLACK_URL` are used across the site but appear blank if none are supplied. The "LOGO_ON_WHITE" is used for general in-page representation, primarily the landing page.  The "LOGO_ON_BLACK" is used for the navbar.  We recommend using an image with a transparent background.  While these logos are not technically required, it is strongly encouraged as they help communicate this application is an official agency website.  

* **Default point of contact**:
`DEFAULT_OWNER_EMAIL` will be the person that gets contacted about new requests if a department is not selected by the requester, or if no liaisons information is supplied to the application. It is a required field.

* **Default point of contact's title**:
`DEFAULT_OWNER_REASON` gets displayed as the reason a request was routed to the default point of contact, and can be simply set to that staff's title/ position within the agency.

* **Users**:
In order for agency staff to log into RecordTrac, RecordTrac must have access to a list of staff provided via a CSV hosted at the `STAFF_URL`. It must be a [delimiter]-separated file with name, email, department name, and phone number columns - in that order. Here's an [example csv](https://github.com/codeforamerica/recordtrac/blob/master/public_records_portal/static/examples/staff.csv). ![Staff csv](/readme/images/staff-csv.png "staff csv")

* **Records liaisons**:
In order for RecordTrac to route a request to the appropriate contact, a list of liaisons must be provided via a CSV hosted at `LIAISONS_URL`. Here's an [example csv](https://github.com/codeforamerica/recordtrac/blob/master/public_records_portal/static/examples/liaisons.csv). ![Liaisons csv](/readme/images/liaisons-csv.png "liaisons csv") 

* Please note that you will have to name your fields according to the examples provided for the staff and liaisons CSV. Once the environment variables are set in Heroku, run `python db_users.py` from the Heroku command line to populate the database with this information.

* **Application URL**:
The `APPLICATION_URL` specifies where you will host RecordTrac on, e.g. `records.youragency.gov`. It is used in e-mail communication and to generate links automatically, so it must be accurate. This can also be the Heroku provided URL to start. It is a required field.

* **Document hosting**:
By default, `HOST_URL` is set to point to Scribd, but if you decide to host documents internally, you would update this field. If using Scribd, you will need to set `SCRIBD_API_KEY` and `SCRIBD_API_SECRET` after setting up a Scribd developer account.

* **E-mail notifications**:
Sign up for a free account with [SendGrid](https://sendgrid.com/user/signup). Set `DEFAULT_MAIL_SENDER` to the e-mail address that you would like to show up in the 'To' field (e.g. `records-donotreply@agency.gov`), set `MAIL_USERNAME` to the SendGrid username you choose, and `MAIL_PASSWORD` to the SendGrid password. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting the `SENDGRID_MONTHLY_LIMIT`.

* **Environment**:
The `ENVIRONMENT` field must be set to `PRODUCTION` once the application is ready to go live. 


### Additional Setup 

Here is additional functionality that is not *required* for a functional instance of RecordTrac, but may be useful.

* **Cron jobs**:
To enable cron jobs, use Heroku add-ons to add a scheduler.
To keep staff data up to date, we recommend maintaining the CSVs (outside of the RecordTrac application), which the application will simply pull from. The task that pulls data from the CSVs to RecordTrac is 'python db_users.py', and can be set as frequently as you'd like. To send e-mail notifications to staff for when a request is due soon or overdue, set up a task 'python send_notifications.py' that runs nightly.

* **Admin list**:
This will enable access to the admin panel of the application. Set `LIST_OF_ADMINS` with a comma separated list of e-mail addresses, i.e. "person1@agency.gov,person2@agency.gov".  

* **Due dates and extensions**:
You can update these variables to reflect your agency's policy. By default, the due date is calculated 10 days from date of submission (`DAYS_TO_FULFILL`), extended 14 additional days if the request is extended (`DAYS_AFTER_EXTENSION`), and notifications for requests that are due soon are calculated 2 days until they are due (`DAYS_UNTIL_OVERDUE`).

* **Spam**:
After setting up Recaptcha and [Akismet](http://akismet.com/plans/) accounts, update the `AKISMET_KEY`, `RECAPTCHA_PUBLIC_KEY`, and `RECAPTCHA_PRIVATE_KEY`, accordingly.

* **Secret key**:
The Flask application requires a `SECRET_KEY` to be set - though a not-so-secret one is provided by default, you can randomly generate a key here: **[update]**.

* **Feedback form**:
You can hook the application up to a Google feedback form by setting the `GOOGLE_FEEDBACK_FORM_ID` to the form ID corresponding to a Google spreadsheet. 


The installation uses a generic set of defaults for email and website copy.  To change these to better reflect your agency's laws and policies, see the [technical documentation](/readme/readme/recordtrac_readme.md). **[UPDATE: or link to "Updating Website Text" in Admin section]**

A complete list of environment variables used in the application can be found in `public_records_portal/__init__.py`.

### Local installation

Instructions for local installation can be found here **(UPDATE)**.




<!-- [![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records) -->
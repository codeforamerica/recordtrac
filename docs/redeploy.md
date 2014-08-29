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

It's worth repeating here (see [Groundwork](/groundwork) above) that the processes RecordTrac supports - managing public record requests - are a core agency function.  RecordTrac should be deployed only under an agency's explicit approval and direct guidance.  There are two types of skills required to redeploy RecordTrac:

*  An agency employee with a policy or legal background - someone who can translate the appropriate laws for RecordTrac.  This may likely be someone in the Clerk's or Attorney's office who already has knowledge of how the agency deals with public records.  For instance, RecordTrac needs to know how long the agency has to respond to a request.
*  A semi-technical user — someone with experience using a terminal or command prompt - should be able to get RecordTrac up and running in a relatively short amount of time (less than a day).

After the initial deployment, RecordTrac will need ongoing maintenance. This can be done by the agency itself or through a qualified contractor(s).  Here are the recommended skills:

*   Python development
*   Front end development (HTML, CSS, JavaScript)

Using the recommended deployment instructions below, the hosting and third-party services should total about $100 per month.  Maintenance service costs are in addition to the hosting costs, and may depend on location and skill. 

If you have problems using RecordTrac, please [open an issue on GitHub](https://github.com/codeforamerica/recordtrac/issues) and let us know what problems or difficulties you encountered in as much detail as you can.

### Deploying on Heroku

To follow the below instructions, you will first need to [install the Heroku toolbelt](https://toolbelt.heroku.com/) on your computer.

Below are example instructions for deploying to Heroku. The process will be similar for other platforms (e.g., Amazon EC2, Red Hat OpenShift).

First, clone the application:

	$ git clone git@github.com:codeforamerica/recordtrac.git

Go into the repo folder:

    $ cd recordtrac

Create a Heroku app:

    $ heroku create

Next, push the code to Heroku:

    $ git push heroku master


#### Create a database
Create the postgres database:

	$ heroku addons:add heroku-postgresql


Access the Heroku command line:

	$ heroku run bash
 
Create the database tables:

	$ python db_setup.py

Technically, that is all you need to get an instance of RecordTrac running with the supplied defaults. But to get a minimum *production-ready* environment running, here's the information you'll need to provide:

#### Set basic environment variables

* **Agency name**: 
Set `AGENCY_NAME` to the name of your agency, which is used across the site (ex. "City of Oakland").

* **Agency logos**: 
`LOGO_ON_WHITE_URL`, `LOGO_ON_BLACK_URL` are used across the site but appear blank if none are supplied. The "LOGO_ON_WHITE" is used for general in-page representation, primarily the landing page.  The "LOGO_ON_BLACK" is used for the navbar.  We recommend using an image with a transparent background.  While these logos are not technically required, it is strongly encouraged as they help communicate this application is an official agency website.  

	Here are example images of both:
	
	![LOGO_ON_WHITE](/public_records_portal/static/examples/logo.png "LOGO_ON_WHITE")
	
	![LOGO_ON_BLACK](/public_records_portal/static/examples/logo_black.png "LOGO_ON_BLACK")

* **Default point of contact**:
`DEFAULT_OWNER_EMAIL` will be the person that gets contacted about new requests if a department is not selected by the requester, or if no liaisons information is supplied to the application. It is a required field.

* **Default point of contact's title**:
`DEFAULT_OWNER_REASON` gets displayed as the reason a request was routed to the default point of contact, and can be simply set to that staff's title/ position within the agency.

* **Application URL**:
The `APPLICATION_URL` specifies where you will host RecordTrac on, e.g. `records.youragency.gov`. It is used in e-mail communication and to generate links automatically, so it must be accurate. This can also be the Heroku provided URL to start. It is a required field.

* **Environment**:
The `ENVIRONMENT` field must be set to `PRODUCTION` once the application is ready to go live. This will enable e-mail notifications, spam filters, and document uploads to Scribd.


#### Set up additional services
* **Spam**:
Set up [Recaptcha](http://www.google.com/recaptcha/intro/) and [Akismet](http://akismet.com/plans/) accounts, then update the `AKISMET_KEY`, `RECAPTCHA_PUBLIC_KEY`, and `RECAPTCHA_PRIVATE_KEY`, accordingly.

* **E-mail notifications**:
Sign up for an account with [SendGrid](https://sendgrid.com/user/signup). Set `DEFAULT_MAIL_SENDER` to the e-mail address that you would like to show up in the 'To' field (e.g. `records-donotreply@agency.gov`), set `MAIL_USERNAME` to the SendGrid username you choose, and `MAIL_PASSWORD` to the SendGrid password. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting the `SENDGRID_MONTHLY_LIMIT`.

* **Document hosting**:
By default, `HOST_URL` is set to point to Scribd, but if you decide to host documents internally, you would update this field. If using Scribd, you will need to set `SCRIBD_API_KEY` and `SCRIBD_API_SECRET` after setting up a [Scribd developer account](http://www.scribd.com/developers).

#### Connect your agency's staff data
* **Users**:
In order for agency staff to log into RecordTrac, RecordTrac must have access to a list of staff provided via a comma-separated file hosted at the `STAFF_URL`. Here's an [example csv](https://github.com/codeforamerica/recordtrac/blob/master/public_records_portal/static/examples/staff.csv). ![staff_csv](/readme/images/staff_csv.png "staff_csv")

	**NOTE: You will have to name your fields according to the example provided, but the order does not matter.**

* **Records liaisons**:
In order for RecordTrac to route a request to the appropriate contact, a list of liaisons must be provided via a comma-separated file hosted at `LIAISONS_URL`. Here's an [example csv](https://github.com/codeforamerica/recordtrac/blob/master/public_records_portal/static/examples/liaisons.csv). ![Liaisons csv](/readme/images/liaisons-csv.png "liaisons csv")

	**NOTE: You will have to name your fields according to the example provided, but the order does not matter.**

 Once the environment variables are set in Heroku, run `python db_users.py` from the Heroku command line to populate the database with this information.


### Additional Setup 

Here is additional functionality that is not *required* for a functional instance of RecordTrac, but may be useful.

* **Cron jobs**:
To enable cron jobs, use Heroku add-ons to add a scheduler.
To keep staff data up to date, we recommend maintaining the CSVs (outside of the RecordTrac application), which the application will simply pull from. The task that pulls data from the CSVs to RecordTrac is `python db_users.py`, and can be set as frequently as you'd like. To send e-mail notifications to staff for when a request is due soon or overdue, set up a task `python send_notifications.py` that runs nightly.

* **Admin list**:
This will enable access to the admin panel of the application. Set `LIST_OF_ADMINS` with a comma separated list of e-mail addresses, e.g. `person1@agency.gov,person2@agency.gov`.  

* **Extensions**:
By default, RecordTrac allows agency staff to extend the request's due date.  If your agency does not allow extensions, they must be manually disabled by removing the relevant code in `_response_widget.html` and `manage_request_city.html`.

* **Due dates and extension times**:
You can update these variables to reflect your agency's policy. By default, the due date is calculated 10 days from date of submission (`DAYS_TO_FULFILL`), extended 14 additional days if the request is extended (`DAYS_AFTER_EXTENSION`), and notifications for requests that are due soon are calculated 2 days until they are due (`DAYS_UNTIL_OVERDUE`).

* **Secret key**:
The Flask application requires a `SECRET_KEY` to be set - though a not-so-secret one is provided by default, you can randomly generate a key [here](randomkeygen.com).

* **Feedback form**:
You can hook the application up to a Google feedback form by setting the `GOOGLE_FEEDBACK_FORM_ID` to the form ID corresponding to a Google spreadsheet. 

A complete list of environment variables used in the application can be found in `/public_records_portal/__init__.py`. These must be configured in Heroku either via the command line (See examples [here](https://devcenter.heroku.com/articles/config-vars)) or their web interface in `dashboard.heroku.com/apps/[yourappname]/settings`

Add an additional [web dyno](https://www.heroku.com/pricing) so that the app is responsive to users.

### Updating website copy

The installation uses a generic set of defaults for email and website copy.  To change these to better reflect your agency's laws and policies, update the copy through the .json files or HTML templates must be modified. 

Most of the copy for RecordTrac can be found in the following .json files:

* **Actions.json**: These describe the actions a member of the public can take to submit a request, as well as the actions to be taken by a agency employee. The text from this file is used for the website's copy. It tells users what will happen when they use a particular feature and who will be able to view the messages or documents uploaded. 
* **Emails.json**: This houses the subject lines for the email notifications that RecordTrac sends out.

All of the HTML files are stored in the `/public_records_portal/templates` folder. The names of the files are mostly self-explanatory. For example to edit the About page at http://records.oaklandnet.com/about, you must modify the 'about.html' file. 

### Updating public URL

We recommend RecordTrac URL uses a subdomain for the official agency website, i.e. `records.[youragency].gov`.  After the domain is secured through the agency, you can link the URL to RecordTrac through [Heroku](https://dashboard.heroku.com/apps/).  Choose the RecordTrac application, select Settings > Domains.

## Local installation

We recommend you use Vagrant to set up RecordTrac locally. Thanks to @vzvenyach for putting together instructions, which we've slightly modified and can be found here: https://github.com/postcode/recordtrac-vagrant

Otherwise, feel free to set up per instructions below.

#### Mac OS X Pre-requisites

This application requires [Postgres](http://www.postgresapp.com/) and Xcode developer tools to be installed.

    /Applications/Postgres.app/Contents/MacOS/bin/psql
    CREATE DATABASE recordtrac;

#### Ubuntu Pre-requisites

Install Postgres, Python, and other required packages.

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y postgresql-9.1 postgresql-server-dev-9.1 python-dev
    sudo apt-get install -y python-pip

#### Postgres & Python

If you are using a standard Postgres installation or from [Homebrew](http://mxcl.github.com/homebrew/) you can also use:

    sudo -u postgres createuser -P -s -e testuser
    sudo -u postgres createdb recordtrac

In a new window:

    git clone git://github.com/postcode/recordtrac.git
    cd recordtrac
    sudo pip install -r requirements.txt
    cp .env.example .env
    sed -i 's/localhost/testuser\:testpwd\@localhost/g' .env

Update relevant fields in .env.

    vi .env

#### Other Accounts

To use e-mail, sign up for a free account with SendGrid and provide the username and password in `MAIL_USERNAME` and `MAIL_PASSWORD`. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting a `SENDGRID_MONTHLY_LIMIT` int value in settings.env.

To be able to catch spammy input, sign up for a free account with [Akismet](http://akismet.com/plans/) and provide the application URL and Akismet key in `APPLICATION_URL` and `AKISMET_KEY`.

### Run locally

If creating the database for the first time, run:

    foreman run python db_setup.py

There are two external data sources the application depends upon: staff directory information (stored in public_records_portal/static/json/directory.json) and information about the departments within the agency (stored in public_records_portal/static/json/departments.json). The data provided is from the City of Oakland, but you should update these files to meet your needs.

To seed the application with user data (as provided in the above two files), requests and responses, run:

    foreman run python db_seed.py

To use the application locally, exit out of python and run:

    foreman start


You should see something similar to:

    2013-05-06 12:16:53 [1776] [INFO] Starting gunicorn 0.17.4
    2013-05-06 12:16:53 [1776] [INFO] Listening at: http://127.0.0.1:5000 (1776)
    2013-05-06 12:16:53 [1776] [INFO] Using worker: sync
    2013-05-06 12:16:53 [1779] [INFO] Booting worker with pid: 1779
    2013-05-06 12:16:53 [1780] [INFO] Booting worker with pid: 1780

Navigate to the url (in this case, http://127.0.0.1:5000) in your browser.

You can now login with any e-mail address and the password 'admin'..
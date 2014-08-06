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

If you have problems using RecordTrac, please open an issue here on GitHub and let us know what problems or difficulties you encountered in as much detail as you can.

### Local Installation

We recommend you use Vagrant to set up RecordTrac locally. Thanks to @vzvenyach for putting together instructions, which we've slightly modified and can be found here: <https://github.com/postcode/recordtrac-vagrant>

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

#### Run locally

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

**EDIT**You can now login with any e-mail address and the password 'admin'.**EDIT**

### Hosted Installation
**TBD**

<!-- [![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records) -->
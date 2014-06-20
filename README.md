RecordTrac 
==============

Hi there!

RecordTrac is an application that some really cool folks at [PostCode](http://www.postcode.io) built and are trying to bring to more government agencies. If you’d like to learn more about the application, you can do so here: http://www.postcode.io/recordtrac If you’re trying to help bring it to your agency, we’d love to help! Generally, the best place to start is by talking to us. If you would like a demo or want something to demo, we’d also be happy to set that up. You can get in touch with us by e-mailing recordtrac@postcode.io. Our core focus right now is getting this adopted in other agencies, with the goal of bringing their FOIA processes online. If you have other uses for it in mind, we’d still love to talk.


## Installation

We recommend you use Vagrant to set up RecordTrac locally. Thanks to @vzvenyach for putting together instructions, which we've slightly modified and can be found here: https://github.com/postcode/recordtrac-vagrant

Otherwise, feel free to set up per instructions below.

### Mac OS X Pre-requisites

This application requires [Postgres](http://www.postgresapp.com/) and Xcode developer tools to be installed.

    /Applications/Postgres.app/Contents/MacOS/bin/psql
    CREATE DATABASE recordtrac;

### Ubuntu Pre-requisites

Install Postgres, Python, and other required packages.

    sudo apt-get update
    sudo apt-get install -y git
    sudo apt-get install -y postgresql-9.1 postgresql-server-dev-9.1 python-dev
    sudo apt-get install -y python-pip

### Postgres & Python

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

### Other Accounts

To use e-mail, sign up for a free account with SendGrid and provide the username and password in `MAIL_USERNAME` and `MAIL_PASSWORD`. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting a `SENDGRID_MONTHLY_LIMIT` int value in settings.env.

To be able to catch spammy input, sign up for a free account with [Akismet](http://akismet.com/plans/) and provide the application URL and Akismet key in `APPLICATION_URL` and `AKISMET_KEY`.

## Run locally

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

You can now login with any e-mail address and the password 'admin'.


<!-- [![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records) -->

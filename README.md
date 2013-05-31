Public Records 
==============

This is a portal to display public record requests to the community and the City of Oakland. It's currently in a research and development phase by the Code for America 2013 Oakland team. We hope to update the documentation soon! In the meantime you can e-mail us at oakland at codeforamerica dot org or [open an issue](https://github.com/codeforamerica/public-records/issues?state=open) if you have any questions.

## Installation

### Mac OS X Pre-requisites

This application requires [Postgres](http://www.postgresapp.com/) and Xcode developer tools to be installed.

    /Applications/Postgres.app/Contents/MacOS/bin/psql
    CREATE DATABASE your_database_name;

### Ubuntu Pre-requisites

Install Postgres, Python, and other required packages.

    sudo apt-get install postgresql-9.1 postgresql-server-dev-9.1 python-dev

### Postgres & Python

If you are using a standard Postgres installation or from [Homebrew](http://mxcl.github.com/homebrew/) you can also use:

        createdb publicrecords

In a new window:

    git clone git://github.com/codeforamerica/public-records.git
    cd public-records
    sudo pip install -r requirements.txt

Save exampleconfig.py as local_config.py and update relevant fields. To test e-mail, sign up for a free account with SendGrid and provide the username and password in MAIL_USERNAME and MAIL_PASSWORD.

## Run locally

If creating the database for the first time, run:

    python
    from public_records_portal import db
    db.create_all()

For database migrations, run:

    alembic upgrade head

To use the application locally, run:

    gunicorn -w 3 -t 180 public_records_portal.prflask:app


You should see something similar to:

    2013-05-06 12:16:53 [1776] [INFO] Starting gunicorn 0.17.4
    2013-05-06 12:16:53 [1776] [INFO] Listening at: http://127.0.0.1:8000 (1776)
    2013-05-06 12:16:53 [1776] [INFO] Using worker: sync
    2013-05-06 12:16:53 [1779] [INFO] Booting worker with pid: 1779
    2013-05-06 12:16:53 [1780] [INFO] Booting worker with pid: 1780

Navigate to the url (in this case, http://127.0.0.1:8000) in your browser.

<!-- [![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records) -->

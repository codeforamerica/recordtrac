Public Records 
==============

This is a portal to manage and display public record requests, built by the Code for America 2013 Oakland team. The project is currently being used by [the City of Oakland](http://www2.oaklandnet.com/Government/o/CityAdministration/PublicRecordsRequest/index.htm), and is extensible to other municipalities. Our docs are available [here](http://codeforamerica.github.io/public-records/docs/1.0.0/). We'd love your feedback. E-mail us at oakland at codeforamerica dot org or [open an issue](https://github.com/codeforamerica/public-records/issues?state=open) if you have any questions.

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

Save settings.env.example as settings.env and update relevant fields.

### Other Accounts

To use e-mail, sign up for a free account with SendGrid and provide the username and password in `MAIL_USERNAME` and `MAIL_PASSWORD`. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting a `SENDGRID_MONTHLY_LIMIT` int value in settings.env.

To be able to catch spammy input, sign up for a free account with [Akismet](http://akismet.com/plans/) and provide the application URL and Akismet key in `APPLICATION_URL` and `AKISMET_KEY`.

## Run locally

If creating the database for the first time, first look up your `SQLALCHEMY_DATABASE_URI` value from settings.env; it will contain a database connection string such as “postgresql://user:password@hostname/dbname”, then run:

    env SQLALCHEMY_DATABASE_URI=<value from settings.env> python
    >>> from public_records_portal import models
    >>> models.db.create_all()

To use the application locally with custom settings, run:

    foreman start -e settings.env

Or to run it with the defaults:
    
    foreman start

You should see something similar to:

    2013-05-06 12:16:53 [1776] [INFO] Starting gunicorn 0.17.4
    2013-05-06 12:16:53 [1776] [INFO] Listening at: http://127.0.0.1:8000 (1776)
    2013-05-06 12:16:53 [1776] [INFO] Using worker: sync
    2013-05-06 12:16:53 [1779] [INFO] Booting worker with pid: 1779
    2013-05-06 12:16:53 [1780] [INFO] Booting worker with pid: 1780

Navigate to the url (in this case, http://127.0.0.1:5000) in your browser.

<!-- [![Build Status](https://travis-ci.org/codeforamerica/public-records.png?branch=master)](https://travis-ci.org/codeforamerica/public-records) -->

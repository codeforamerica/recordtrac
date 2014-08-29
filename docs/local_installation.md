## Local installation

We recommend you use a virtual environment to set up RecordTrac locally. More details can be found in [this howto](https://github.com/codeforamerica/howto/blob/master/Python-Virtualenv.md).


This application requires [PostgreSQL](http://www.postgresapp.com/). For help getting started with PostgreSQL and creating a database, you can refer to [this howto](https://github.com/codeforamerica/howto/blob/master/PostgreSQL.md). Name your database 'recordtrac'.

Inside your virtual environment:

    git clone git://github.com/postcode/recordtrac.git
    cd recordtrac
    sudo pip install -r requirements.txt

Save .env.example as .env, and update relevant fields in .env.

#### Other Accounts

To use e-mail, sign up for a free account with SendGrid and provide the username and password in `MAIL_USERNAME` and `MAIL_PASSWORD`. We assume your monthly email limit is 40,000 sends (Sendgrid's Bronze account level), but you can change this by setting a `SENDGRID_MONTHLY_LIMIT` int value in your .env file.

To be able to catch spammy input, sign up for a free account with [Akismet](http://akismet.com/plans/) and provide the application URL and Akismet key in `APPLICATION_URL` and `AKISMET_KEY`.

### Run locally

If creating the database for the first time, run:

    foreman run python db_setup.py

To seed the application with user data, requests and responses, run:

    foreman run python db_users.py
    foreman run python db_seed.py

To use the application locally, run:

    foreman start


You should see something similar to:

    2013-05-06 12:16:53 [1776] [INFO] Starting gunicorn 0.17.4
    2013-05-06 12:16:53 [1776] [INFO] Listening at: http://127.0.0.1:5000 (1776)
    2013-05-06 12:16:53 [1776] [INFO] Using worker: sync
    2013-05-06 12:16:53 [1779] [INFO] Booting worker with pid: 1779
    2013-05-06 12:16:53 [1780] [INFO] Booting worker with pid: 1780

Navigate to the url (in this case, http://127.0.0.1:5000) in your browser.

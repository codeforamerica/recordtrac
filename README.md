[ ![Codeship Status for nycrecordswebdev/recordtrac](https://codeship.com/projects/e1c59fe0-9c47-0133-fe2b-3604d537a8d3/status?branch=master)](https://codeship.com/projects/127075)

#NYC OpenRecords
This is the home page for documentation for the **NYC OpenRecords** application.

* [What is RecordTrac](#what-is-recordtrac)
* [How to create a new RecordTrac app](#how-to-create-a-new-recordtrac-app-for-your-agency)
* [Technical details and developer documentation](#technical-details)
* [How to use RecordTrac](#how-to-use-recordtrac-as-a-requester)

For help contact [Code for America](http://www.codeforamerica.org/apps/recordtrac)

##What is RecordTrac?
RecordTrac is a public record request management tool for government agencies.
![RecordTrac](/docs/images/generic_request.png "RecordTrac")
This web application allows government employees manage, respond to, and fulfill incoming requests.  It also provides a quick, simple way for individuals to submit public record requests. RecordTrac displays all requests and responsive documents so that members of the public may find what they need without submitting additional public record requests.

[More about RecordTrac...](/docs/about.md)

##[How to create a new RecordTrac app for your agency](/docs/redeploy.md)
* Groundwork
* Best Practices
* Redeploy on Heroku

###To create a development environment, you can  [install RecordTrac locally](/docs/local_installation.md).

##Technical details
RecordTrac is primarily a Python application built on a backend Flask framework and a frontend Bootstrap framework.

RecordTrac is compatible with most modern browsers, including Internet Explorer 8 and above.

###Platform pieces
* [Flask 0.10](http://flask.pocoo.org/) is used as the backend Python framework.
* [Bootstrap 2.3.2](http://getbootstrap.com/2.3.2) is used as the frontend HTML/CSS/JS framework.
* [Postgres 9.3.0](http://www.postgresapp.com/) is used to manage the database.
* [Python 2.7.5](http://www.python.org/getit) is used as the foundational programming language.

###Plugins
* [Font Awesome 3.2.1](http://fortawesome.github.io/Font-Awesome) is used to render all the icons on the site.
* A number of Javascript libraries like [Backbone.js 1.1.2](http://backbonejs.org/#) are used, primarily for the search function.

###Service dependencies
* [SendGrid](http://sendgrid.com/) is used for all email notifications about requests.
* [Akismet](http://akismet.com/) is used as a spam filter.
* [Captcha](http://www.captcha.net/) is used to allow requesters to override the spam filter if necessary.
* [Mozilla Persona](https://login.persona.org/) is used to manage user authentication and password management.

###Feature backlog
Issues and feature backlog are tracked through [GitHub issues](https://github.com/codeforamerica/recordtrac/issues).

###Developer documentation
* [Browse full source code on GitHub](https://github.com/codeforamerica/recordtrac)
* [Technical docs](http://codeforamerica.github.io/recordtrac/docs/2.0.0/technical-docs.html)

##How to use RecordTrac... as a requester
* [Search for a record](/docs/requester.md)
* [Make a new request](/docs/requester.md#make-a-request)

##How to use RecordTrac... as an agency employee
* [Search for a record](/docs/responder.md)
* [Manage your request list](/docs/responder.md#manage-your-request-list)
* [Make a new request](/docs/responder.md#make-a-new-request)
* [Respond to a request](/docs/responder.md#respond-to-a-request)
* [Admin](/docs/admin.md)

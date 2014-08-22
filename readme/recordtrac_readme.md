#RecordTrac
This is the home page for documentation for the **RecordTrac** application.

For help contact **oakland |@| codeforamerica.org**

##What is RecordTrac?
RecordTrac is a public record request management tool for government agencies.
![RecordTrac](https://github.com/codeforamerica/recordtrac/raw/readme/readme/generic_request.png "RecordTrac")  
This web application allows government employees manage, respond to, and fulfill incoming requests.  It also provides a quick, simple way for individuals to submit public record requests. RecordTrac displays all requests and responsive documents so that members of the public may find what they need without submitting additional public record requests.

##How to create a new RecordTrac app for your agency
* [Groundwork](/readme/redeploy.md)
* [Best Practices](/redeploy.md#best-practices)
* [Redeploy](/redeploy.md#redeploy)

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
* [Askimet](http://akismet.com/) is used as a spam filter.
* [Captcha](http://www.captcha.net/) is used to allow requesters to override the spam filter if necessary.
* [Mozilla Persona](https://login.persona.org/) is used to manage user authentication and password management.

###Feature backlog
Issues and feature backlog are tracked through [GitHub issues](https://github.com/codeforamerica/recordtrac/issues).

##Developers

###API Documentation
* [API](http://codeforamerica.github.io/public-records/docs/1.0.0/api.html)

###Source Code
* [Source Code](https://github.com/codeforamerica/recordtrac)
* [Issue Tracker](https://github.com/codeforamerica/recordtrac/issues)

###Developer Documentation
* [Db Helpers](http://codeforamerica.github.io/public-records/docs/1.0.0/db-helpers.html)
* [Departments](http://codeforamerica.github.io/public-records/docs/1.0.0/departments.html)
* [Models](http://codeforamerica.github.io/public-records/docs/1.0.0/models.html)
* [Notifications](http://codeforamerica.github.io/public-records/docs/1.0.0/notifications.html)
* [PRR](http://codeforamerica.github.io/public-records/docs/1.0.0/prr.html)

##How to use RecordTrac... as a requester
* [Search for a record](/requester.md)
* [Make a new request](/requester.md#make-a-request)

##How to use RecordTrac... as an agency employee
* [Search for a record](/responder.md)
* [Manage your request list](/responder.md#manage-your-request-list)
* [Make a new request](/responder.md#make-a-new-request)
* [Respond to a request](/responder.md#respond-to-a-request)
* [Admin](/admin.md)

##About
* [Why was RecordTrac built?](/about.md#why-was-recordtrac-built)
* [Design principles](/about.md#design-principles)
* [Research and references](/about.md#research-and-references)
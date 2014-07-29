#RecordTrac
This is the home page for documentation for **RecordTrac** app.


For help contact **oakland|@|codeforamerica.org**

##What is RecordTrac?
![RecordTrac](./readme/generic_request.png "RecordTrac")RecordTrac is a public record request management tool for government agencies.  This web application allows government employees manage, respond to, and fulfill incoming requests.  It also provides a quick, simple way for individuals to submit public record requests. RecordTrac displays all requests and responsive documents so that members of the public may find what they need without submitting additional public record requests.


##How to create a new RecordTrac app for your agency
###Groundwork
###Best Practices
###Redeploy
##Technical details
RecordTrac is primarily a Python application built on a backend Flask framework and a frontend Bootstrap framework.

RecordTrac is compatible with most modern browsers, including Internet Explorer 8 and above.
###Platform pieces
Flask 0.10 is used as the backend Python framework.
Bootstrap 2.3.2 is used as the frontend HTML/CSS/JS framework.
Postgres 9.3.0 is used to manage the database.
Python 2.7.5 is used as the foundational programming language.
###Plugins
Font Awesome 3.2.1 is used to render all the icons on the site.
A number of Javascript libraries like Backbone.js 1.1.2 are used, primarily for the search function.
###Service dependencies
SendGrid is used for all email notifications about requests.
Askimet is used as a spam filter.
Captcha is used to allow requesters to override the spam filter if necessary.
Mozilla Persona is used to manage user authentication and password management.
###Feature backlog
Issues and feature backlog are tracked through GitHub issues.
##Developers
###API Documentation
API
###Source Code
Source Code (Github)
Issue Tracker (Github)
###Developer Documentation
Db Helpers
Departments
Models
Notifications
PRR
##About
Why was RecordTrac built?
Design Principles
Research and references
##How to use RecordTrac... as a requester
Search for a record
Make a new request
##How to use RecordTrac... as an agency employee
Search for a record
Make a new request
Respond to a request
Manage your request list
Admin

# RecordTrac's Admin Features

## Description 

RecordTrac’s administrative controls allows the users to:

* [Edit or remove request text](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#how-to-remove-or-edit-a-request)
* [Remove a record](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#how-to-remove-a-record)
* [Edit or remove the text of a note](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#how-to-remove-or-edit-a-note)
* [Edit or remove a question or answer](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#how-to-remove-or-edit-a-question-and-answer-exchange)
* [Add or remove a Public Records Request (PRR) liaison](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#how-to-change-the-official-public-records-request-prr-liaison-for-a-department)
* [Update your RecordTrac website text](https://github.com/codeforamerica/recordtrac/blob/readme/readme/admin.md#updating-website-copy)

The administrative controls allows the user to permanently delete records, requests, and notes from the database. Because of this, administrative access should be restricted to a small number of users. 


## Best Practices

Content should only be removed or edited if sensitive or confidential information is revealed. If this happens, you should:

* Save a copy of the original message. (This will have to be done outside of RecordTrac. There is no way to hide a message from public view.) 
* Edit the message to indicate why it needs to be removed. 
* Notify the requester why their post or answer was removed.
* Provide guidance to the requester on how they can get the record they need. 

If a staff member enters information incorrectly, simply add a note explaining the mistake. 

If a member of the public enters incorrect information,  the requester (or a staff member) can add a note correcting the mistake. 

Sometimes it’s necessary to create a new request. If a new request must be created, we suggest you do the following:

* Create a new request with the proper information.
* In the old request, include a note explaining what is wrong with it and a link to the new request.
* Close out the old request.
* In the new request, reference and/or provide a link to the old request. 

Although RecordTrac has a spam filter, every once in a while it may receive spam. When confronted with spam, close the request with a note indicating why it is not a public records request.  If there is a large amount of spam requests, it is appropriate to simply remove the spam. 

If a record needs to be removed. It not only has to be deleted on RecordTrac, it has to be removed from Scribd as well. 

## How to Remove or Edit a Request

To remove or edit a request, visit records.oaklandnet.com/admin/requestview. 

image::admin_request.png[]

A description of the fields in the table displayed can be found below:

* Id: Unique ID assigned to each request.
* Text: Entire text of public records request.
* Date Created: The date the request was entered in RecordTrac.
* Status: Status of the records request, namely whether it’s open, closed, due soon, or overdue.

Clicking on the trashcan icon permanently deletes an entire request.

image::admin_delete_request.png[]

Clicking on the pencil icon will allow you to edit a request. 

image::admin_edit_request.png[]

## How to Remove a Record

To remove a record, visit records.oaklandnet.com/admin/recordreview.

image::admin_record.png[]

You can only remove a record, not "edit" any of the fields.  Records include web links, uploaded electronic documents, and instructions on how to view or pick up copies of a record. 

A description of the fields in the table displayed can be found below:

* ID: Unique ID assigned to each request.
* Filename: Name of electronic record uploaded to RecordTrac. 
* URL: Web address provided to requester.
* Download URL: Web address where you can automatically download the record. 
* Access: Instructions on how to view or pick up copies of a record

Click on the trashcan icon to permanently delete the record from RecordTrac. You must also delete the record from the hosted location.  For example, if you are using Scribd, it must be deleted from the Scribd account.  

image::admin_delete_record.png[]

## How to Remove or Edit a Note

To edit or remove a note, visit records.oaklandnet.com/admin/noteview.

image::admin_note.png[]

A description of the fields in the table displayed can be found below:

* ID: Unique ID assigned to each request.
* Text: Entire text of the note.
* Date Created: The date the note was created. 

Click on the trashcan icon to permanently delete the note from RecordTrac. 

image::admin_delete_note.png[]

Clicking on the pencil icon will allow you to edit the text of a note.

image::admin_edit_note.png[]

## How to Remove or Edit a Question and Answer Exchange

To remove posted questions and/or answers, navigate to the "Q A" tab.

image::admin_qa.png[]

A description of the fields in the table displayed can be found below:

* ID: Unique ID assigned to each request.
* Question: Entire text of the question asked by city staff.
* Answer: Entire response of question provided by member of the public. 
* Date Created: The date the exchange was created

Clicking on the trashcan icon permanently deletes the entire question and answer exchange.

image::admin_delete_qa.png[]

Clicking on the pencil icon will allow you to edit the text of the question and answer exchange. 

image::admin_edit_qa.png[]

## How to Change the official Public Records Request (PRR) liaison for a department

To change the Public Record Request (PRR) liaision, or the individual responsible for responding for responding to public records requests for a particular department, visit records.oaklandnet.com/admin/userview.

image::admin_prr_liaison.png[]

You will see a  list of all employees contained in the official city directory. 

A description of the fields in the table displayed can be found below:

* Contact for: Listing of departments the city employee is the PRR liaison for. 
* Back-up for: Listing of departments the city employee is a backup for. 
* Alias: Name of city employee.

Clicking on the trashcan icon permanently deletes the user. 


To edit the user’s information, click on the pencil icon. You then have the opportunity to edit the user's name, email address, phone number, and which department they are the contact or backup for. 

image::admin_edit_prr_liaison.png[]

Enter one of the department names in the “Contact for” or “Backup For” field. If a user is responsible for multiple departments, separate the department names with a comma.

You can find a list of departments **insert explanation here**

You can delete a user by clicking on the trashcan icon.

image::admin_delete_user.png[]

## Updating Website Text

The web copy is not managed through the admin section. To update the copy on the website, the .json files or HTML templates must be modified. 

The copy for the web application can be found in the following .json files:

* Action.json describes the actions a member of the public can take to submit a request, as well as the actions to be taken by a city employee. The text from this file is used for the website's copy. It tells users what will happen when they use a particular feature and who will be able to view the messages or documents uploaded. 
* Notcityrecords.json: When a member of the public types in a particular word or phrase pertaining to a record not possessed by the City of Oakland while submitting a request, a message pops up explaining to the user they need to contact another municipality. This file keeps track of all the phrases and messages.
* Prr_help.json: This is the copy displayed on the "New Request" page. It includes tips for submitting a public records request, as well as three examples of public records requests. 
* Tutorial.json: The copy for the tutorial can be found here. 

All of the HTML files are stored in the templates folder. The names of the files are pretty self-explanatory, and it is simple to find the file that corresponds to each webpage. For example to edit the About page at http://records.oaklandnet.com/about, you must modify the 'about.html' file. 


## Changing Passwords

Passwords are not managed through the admin section. City employees are able to change their own passwords, if they do the following:

Go to http://records.oaklandnet.com/reset_password[records.oaklandnet.com/reset_password].

image::reset_password.png[]

A temporary password will be sent via email.

Use the temporary password to log into the system.

Go to http://records.oaklandnet.com/update_password to change your password.

image::update_password.png[]

Once you click the green “Update” button your password will change. 

## Checking Status of RecordTrac

image::app_status.png[]

Developers at Code for America created a quick way for adminstrators to check on the status of the application. Visit http://records.oaklandnet.com/.well-known/status[records.oaklandnet.com/.well-known/status] to get a quick confirmation of whether the app is working.

If the status is 'ok,' it means the app is working properly and users should not encounter any problems.

The number next to SendGrid is the percentage of its email quota the application has used this month. If it is close to 100, then the City is close to hitting its email quotas for the month and may be charged for each additional email. 

The dependencies section lists the web applications used by RecordTrac. Askismet is the spam filter. Scribd is where all uploaded documents are hosted. SendGrid sends out the email notifications and Postgres is where all of the data is stored. 


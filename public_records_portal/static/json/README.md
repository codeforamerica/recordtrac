These JSON files are being used to hold:

- Copy for web application 
  - Action.json describes the actions a member of the public can take to submit a request, as well as the actions to be taken by a city employee. The text from this file is used for the website's copy. It tells users what will happen when they use a particular feature and who will be able to view the messages or documents uploaded. 
  - Notcityrecords.json: When a member of the public types in a particular word or phrase pertaining to a record not possessed by the City of Oakland while submitting a request, a message pops up explaining to the user they need to contact another municipality. This file keeps track of all the phrases and messages.
  -Prr_help.json: This is the copy displayed on the "New Request" page. It includes tips for submitting a public records request, as well as three examples of public records requests. 
  -Tutorial: The copy for the tutorial can be found here. 


- City Directories and contact information
  - Directory.json: The file contains the name and contact information for all City of Oakland employees. It is used to provide contact information to the public on the web page containing the request and responses from city employees. 
  - Departments.json: This file contains the list of Public Records Request (PRR) Liaisons and their backup. (The PRR Liaisons are the ones responsible for fulfilling public records requests in the City of Oakland.) The liaisons are referenced using their email addresses. The file also contains a "Doc Types" field. These are the types of documents you can find within the department. 
  - List_of_departments.json: This is a list of all the department in the City of Oakland. This list is generated from the Directory.json file. 
  - Doctypes.json lists the types of documents that can found in each department. It is generated using the Directory.json file. 
  - Do_not_email.json: If there is a city employee who should not receive email notifications, they are added to this list. 

Emails.json is a comprehensive list of they type of email notifications sent by this web application. It also includes information on who receives each notification and the email subject lines. 




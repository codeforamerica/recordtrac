var casper = require('casper').create({
    viewportSize : {width : 800, height : 600},
    verbose: true,
    logLevel: "debug",
});

casper.start("http://localhost:3000", function userInterface() {
    this.capture("index.png");
});

casper.thenOpen('http://records.oaklandnet.com/request/1', function userInterface() {
    this.captureSelector("request1response.png", "#responses-container");
    this.captureSelector("request1request.png", "#request-container");
 });

// casper.thenOpen('http://records.oaklandnet.com/public/request/954', function userInterface() {
//     this.captureSelector("public_add_a_note.png", "#public_note");
//  });

casper.thenOpen('http://records.oaklandnet.com/new', function userInterface() {
    this.captureSelector("new_request_form.png", "#submitRequest");
 });

casper.thenOpen('http://records.oaklandnet.com/api/request/1', function userInterface() {
	var fs = require('fs');
    fs.write('api.json', this.getPageContent());
 });


casper.run();
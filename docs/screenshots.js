var casper = require('casper').create({
    viewportSize : {width : 800, height : 600},
    verbose: true,
    logLevel: "debug",
});

casper.start("http://localhost:5000", function userInterface() {
    this.capture("index.png");
});

casper.thenOpen('http://localhost:5000/request/1', function userInterface() {
    this.captureSelector("request1response.png", "#responses-container");
    this.captureSelector("request1request.png", "#request-container");
 });

casper.thenOpen('http://records.oaklandnet.com/api/request/1', function userInterface() {
	var fs = require('fs');
    fs.write('api.json', this.getPageContent());
 });


casper.run();
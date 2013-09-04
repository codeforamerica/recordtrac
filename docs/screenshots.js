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

casper.run();
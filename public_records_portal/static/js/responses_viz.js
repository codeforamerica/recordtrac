var margin = {top: 30, right: 20, bottom: 30, left: 40},
    height = 250 - margin.top - margin.bottom,
    width = $('#responses-freq-viz').parent().width() - margin.left - margin.right;

var formatYAxis = d3.format("f");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(formatYAxis)
    .ticks(5);

var shortDeptNames = {
    "Office of the Mayor":                  'Mayor',
    "City Administrator":                   'City Admin',
    "City Clerk":                           'Clerk',
    "City Auditor":                         'Auditor',
    "City Attorney":                        'Attorney',
    "Parks and Recreation":                 'Parks & Rec',
    "Public Works Agency":                  'Public Works',
    "Department of Planning and Building":  'Planning',
    "Fire Department":                      'Fire',
    "Library Services":                     'Library',
    "Office of Controller and Treasury":    'Treasury',
    "Contracts and Compliance":             'Contracts',
    "Information Technology (IT)":          'IT',
    "Office of Neighborhood Investment":    'Neighborhood',
    "Health and Human Services":            'Health',
    "Human Resources":                      'HR',
    "Budget and Revenue - Revenue Division":            'Budget',
    "Council District 1 - Dan Kalb":        'D1',
    "Council District 2 - Pat Kernighan":   'D2',
    "Council District 3 - Lynette Gibson McElhaney":    'D3',
    "Council District 4 - Libby Schaaf":    'D4',
    "Council District 5 - Noel Gallo":      'D5',
    "Council District 6 - Desley Brooks":   'D6',
    "Council District 7 - Larry Reid":      'D7',
    "Council At Large - Rebecca Kaplan":    'Council',
    "Oakland Police Department":            'Police'
}



// Create Frequency Graph for department requests volume
$(function(){

  var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) {
      return d.department + "<br /><center><div style='font-weight: normal; font-size: 12px; margin-top:5px'>Requests: <span style='color:#FB991B'>" + d.freq + "</span></div></center>";
    });

  var svg = d3.select("#responses-freq-viz").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.call(tip);

  d3.json(viz_data_freq, function(error, json) {
    // if (error) return console.warn("Didn't load responses_data.json properly.");
    data = viz_data_freq;
    x.domain(data.map(function(d) { return shortDeptNames[d.department]; }));
    y.domain([0, d3.max(data, function(d) { return d.freq; })]);

    // X-Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .style("width", "50px")
        .attr("text-anchor", "end")
        .attr("textLength", "10");

    svg.selectAll("text")

    // Y-Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em");

    // Heading Text
    svg.append("text")
        .attr("x", (width/4))
        .attr("y", -10)
        .style("font-size", "14px")
        .style("fill", "#333333")
        .style("font-weight", "bold")
        .text("Requests by Department");

    // draw bars vectors
    svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(shortDeptNames[d.department]); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.freq); })
        .attr("height", function(d) { return height - y(d.freq); })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

  });
});



// ----- Graph 2 ----- 
// ===================

var margin = {top: 30, right: 20, bottom: 30, left: 40},
    height = 250 - margin.top - margin.bottom,
    width = $('#responses-time-viz').parent().width() - margin.left - margin.right;

var xResponseTime = d3.scale.linear()
    .rangeRoundBands([0, width], .1);

var yDepartments = d3.scale.ordinal()
    .range([0, height]);

var xResponseTimeAxis = d3.svg.axis()
    .scale(xResponseTime)
    .orient("bottom");

var yDepartmentsAxis = d3.svg.axis()
    .scale(yDepartments)
    .orient("left")
    .tickFormat(formatYAxis)
    .ticks(5);



// Create Average Response Time Graph 
$(function() {

  var svgNext = d3.select("#responses-time-viz").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var tipNext = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) {
      return "Frequency: <span style='color:red'>" + d.time + "</span>";
    });

  svgNext.call(tipNext);

  d3.json("static/json/responses_time_data.json", function(error, json) {
    if (error) return console.warn("Didn't load responses_time_data.json properly.");
    data = json;
    xResponseTime.domain([0, d3.max(data, function(d) { return d.time; })]);
    yDepartments.domain(data.map(function(d) { return d.department; }));


    // xAxis -- Time responses graph
    svgNext.append("g")
        .attr("class", "x axis")
        .attr("transform", "rotate(-90)")
        .attr("transform", "translate(0," + height + ")")
        .call(xResponseTimeAxis);


    // yAxis -- Depatments listings
    svgNext.append("g")
        .attr("class", "y axis")
        .append("text")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end");

    svgNext.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return xResponseTime(d.time); })
        .attr("width", function(d) { return width - xResponseTime(d.time); })
        .attr("y", function(d) { return yDepartments(shortDeptNames[d.department]); })
        .attr("height", yDepartments.rangeBand())
        .on('mouseover', tipNext.show)
        .on('mouseout', tipNext.hide);



        // .attr("x", function(d) { return x(shortDeptNames[d.department]); })
        // .attr("width", x.rangeBand())
        // .attr("y", function(d) { return y(d.freq); })
        // .attr("height", function(d) { return height - y(d.freq); })

  });
});


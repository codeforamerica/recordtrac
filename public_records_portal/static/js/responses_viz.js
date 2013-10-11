var margin = {top: 20, right: 20, bottom: 30, left: 40},
    height = 200 - margin.top - margin.bottom,
    width = $('#responses-viz').parent().width() - margin.left - margin.right;

var formatYAxis = d3.format("f");

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .ticks(0)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(formatYAxis)
    .ticks(5);



// Create Frequency Graph for department requests volume
$(function(){

  // var retreived_json = JSON.parse('static/json/responses_data.json');

  // var top3, bot3 = [], []

  // for (i=0; i<retreived_json.length; i++) {
  //   if retreived_json[i] > top3

  // }

  var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-10, 0])
    .html(function(d) {
      return "Frequency: <span style='color:red'>" + d.freq + "</span>";
    });

  var svg = d3.select("#responses-viz").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.call(tip);

  d3.json(viz_data, function(error, json) {
    if (error) return console.warn("Didn't load responses_data.json properly.");
    data = json;
    x.domain(data.map(function(d) { return d.department; }));
    y.domain([0, d3.max(data, function(d) { return d.freq; })]);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("");

    svg.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.department); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.freq); })
        .attr("height", function(d) { return height - y(d.freq); })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

  });

});






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
    x.domain(data.map(function(d) { return d.department; }));
    y.domain([0, d3.max(data, function(d) { return d.time; })]);

    svgNext.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svgNext.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("");

    svgNext.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.department); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.time); })
        .attr("height", function(d) { return height - y(d.time); })
        .on('mouseover', tipNext.show)
        .on('mouseout', tipNext.hide);

  });

});


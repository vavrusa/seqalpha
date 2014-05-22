$(function () {

    jQuery.ratioChart = function (parent, data) {

     var margin = 30;

        var svg = jQuery.createChartContainer(parent, 'ratio');
        var svg_owner = svg[0][0];
        svg = svg.append("g")
            .attr("transform", "translate(" + 2*margin + "," + margin/2 + ")");


        var width = svg_owner.width.baseVal.value - 2*margin;
        var height = svg_owner.height.baseVal.value - 2*margin;

        var formatPercent = d3.format(".1%");
        var color = d3.scale.category20();

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
    .tickFormat(formatPercent);

data.forEach(function (d) {
  d.frequency = +d.frequency;
});


x.domain(data.map(function(d) { return d.key; }));
  y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

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
      .text("Frequency");


        var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function (d) {
            return "translate(" + x(d.key) + "," + y(d.frequency) + ")";
        });

        bar.append("rect")
            .attr("width", x.rangeBand())
            .attr("height", function(d) { return height - y(d.frequency); })
            .style("fill", function (d) {
            return color(d.key);
        });

        bar.append("text")
            .attr("dy", ".75em")
            .attr("y", '-1em')
            .attr("x", x.rangeBand() / 2)
            .attr("text-anchor", "middle")
            .text(function (d) {
            return formatPercent(d.frequency);
        });

  }
});

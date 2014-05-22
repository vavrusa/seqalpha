$(function () {

    jQuery.histogramChart = function (parent, values) {

        var svg = jQuery.createChartContainer(parent, 'histogram');
        var svg_owner = svg[0][0];

        var margin = 30;
        var width = svg_owner.width.baseVal.value - 2*margin;
        var height = svg_owner.height.baseVal.value - margin;

        /* Resort values. */
        values.sort(function (a, b) {
            return a - b;
        });

        // A formatter for counts.
        var formatCount = d3.format(",.0f");

        var x = d3.scale.linear()
            .domain([values[0], values[values.length - 1]])
            .range([0, width]);

        // Generate a histogram using twenty uniformly-spaced bins.
        var data = d3.layout.histogram()
            .range([values[0], values[values.length - 1]])
            .bins(x.ticks(10))
        (values);

        var y = d3.scale.linear()
            .domain([0, d3.max(data, function (d) {
            return d.y;
        })])
            .range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var bar = svg.selectAll(".bar")
            .data(data)
            .enter().append("g")
            .attr("class", "bar")
            .attr("transform", function (d) {
            return "translate(" + x(d.x) + "," + y(d.y) + ")";
        });

        bar.append("rect")
            .attr("x", 1)
            .attr("width", x(values[0] + data[0].dx) - 1)
            .attr("height", function (d) {
            return height - y(d.y);
        });

        bar.append("text")
            .attr("dy", ".75em")
            .attr("y", 6)
            .attr("x", x(values[0] + data[0].dx) / 2)
            .attr("text-anchor", "middle")
            .text(function (d) {
            return formatCount(d.y);
        });

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);
    }

});
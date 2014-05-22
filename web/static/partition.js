$(function () {

    jQuery.partitionChart = function (parent, root) {

        var svg = jQuery.createChartContainer(parent, 'partition');
        var svg_owner = svg[0][0];
        var width = svg_owner.width.baseVal.value;
        var height = svg_owner.height.baseVal.value;

        var x = d3.scale.linear()
            .range([0, width]);

        var y = d3.scale.linear()
            .range([0, height]);

        var color = d3.scale.category20c();

        var partition = d3.layout.partition()
            .value(function (d) {
            return d.value;
        });

        var nodes = partition.nodes(root);

        var g = svg.selectAll("g")
            .data(nodes)
            .enter().append("svg:g")
            .attr("transform", function (d) {
            return "translate(" + x(d.y) + "," + y(d.x) + ")";
        })
            .on("click", click);

        var kx = width / root.dx,
            ky = height / 1;

        g.append("svg:rect")
            .attr("width", root.dy * kx)
            .attr("height", function (d) {
            return d.dx * ky;
        })
            .style("fill", function (d) {
            return color(d.depth);
        })
            .attr("class", function (d) {
            return d.children ? "parent" : "child";
        });

        g.append("svg:text")
            .attr("transform", transform)
            .attr("dy", ".35em")
            .style("opacity", function (d) {
            return d.dx * ky > 12 ? 1 : 0;
        })
            .text(function (d) {
            return d.name;
        })

        d3.select(window)
            .on("click", function () {
            click(root);
        })

        function click(d) {
            if (!d.children) return;

            kx = (d.y ? width - 40 : width) / (1 - d.y);
            ky = height / d.dx;
            x.domain([d.y, 1]).range([d.y ? 40 : 0, width]);
            y.domain([d.x, d.x + d.dx]);

            var t = g.transition()
                .duration(d3.event.altKey ? 7500 : 750)
                .attr("transform", function (d) {
                return "translate(" + x(d.y) + "," + y(d.x) + ")";
            });

            t.select("rect")
                .attr("width", d.dy * kx)
                .attr("height", function (d) {
                return d.dx * ky;
            });

            t.select("text")
                .attr("transform", transform)
                .style("opacity", function (d) {
                return d.dx * ky > 12 ? 1 : 0;
            });

            d3.event.stopPropagation();
        }

        function transform(d) {
            return "translate(8," + d.dx * ky / 2 + ")";
        }
    }

});
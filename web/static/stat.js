$(function () {

    /* Calculate series score median. */
    jQuery.median = function median(series) {
        var half = Math.floor(series.length / 2);
        if(series.length % 2) {
            return series[half];
        }
        return (series[half-1] + series[half]) / 2.0;
    }

    /* Create statistic chart container. */
    jQuery.createChartContainer = function (parent, name) {
        return d3.select(parent.toArray()[0]).append("svg")
                       .attr("width", 500)
                       .attr("height", 300)
                       .attr("class", name + " chart");
    }

});
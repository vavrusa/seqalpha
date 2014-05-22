$(function () {

	/* Ratio chart for FASTA match/total ratio. */
	function createFastaCharts(parent, match, total) {

	    var container = $('<div class="subresult"><h4>Rule match/mismatch ratio</h4></div>');
        parent.after(container);

        /* Create bar chart. */
	    var data = [ {'key':'Match', 'frequency':match/total},
	                 {'key':'Mismatch', 'frequency': 1.0 - match/total}
	               ];
        jQuery.ratioChart(container, data);
	}

	jQuery.fastaTable = function fastaTable(table, task) {

		/* Hook to FASTA results only. */
		if (!table.hasClass('result_fasta')) {
		    return;
		}

        /* Ratio chart with match/mismatch ratio. */
        createFastaCharts(table, task.result[0][1], task.result[0][2]);
	}

});


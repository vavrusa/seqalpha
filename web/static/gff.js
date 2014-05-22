$(function () {

	/* Get single series (f.e. getSeries([ [1,a], [2,b], [3,c] ], 0) would yield [1,2,3]). */
    function getSeries(arr, index) {
        var data = [];
		for (i in arr) {
			data.push(parseFloat(arr[i][index]));
		}
		return data;
    }

    function splitPartition(part, name_left, name_right) {
        /* Partition data into tree. */
        var left = []
        var right = []
        /* Calculate median. */
        var series = getSeries(part.children, 'value');
        series.sort();
        var median = jQuery.median(series);
        /* Redistribute partitions. */
        for (var i in part.children) {
            if (part.children[i].value < median) {
                left.push( part.children[i] );
            } else {
                right.push( part.children[i] );
            }
        }
        /* Append. */
        part.children = [ { 'name': name_left, children: left }, { 'name': name_right, children: right } ]
    }

    function partitionResult(result) {
        /* [ Accession, Score ] -> [ Partition, Accession, Score ] */

        /* Insert raw data. */
        var data = { 'name': 'Whole set', 'children': [] }
        for (var i in result) {
            data.children.push( {'name': result[i][0], 'value': result[i][1] } );
        }

        /* Split into lower and upper median. */
        splitPartition(data, '1st half', '2nd half');

        /* Split into lower and upper quartiles. */
        splitPartition(data.children[0], '1st quartile', '2nd quartile');
        splitPartition(data.children[1], '3rd quartile', '4th quartile');

        return data;
    }

    function createScoreCharts(table, fields, result) {

        /* Check numeric series existence in second column. */
        if (isNaN(result[0][1])) {
            return;
        }

        var series = getSeries(result, 1);
        var container = $('<div />');
        table.after(container);

        /* Create partitioned table for reasonable amount of data. */
        if (series.length < 500) {
            var left = $('<div class="subresult" style="float: left;"><h4>Table results split</h4></div>');
                container.append(left);
                jQuery.partitionChart(left, partitionResult(result));
        }

        /* Create histogram. */
        var right = $('<div class="subresult"><h4>' + fields[1] + ' histogram</h4></div>');
        container.append(right);
        jQuery.histogramChart(right, series);

        /* Clear. */
        container.append('<div style="clear: both;" />');
    }

    /* Make URL from accession number. */
    function accessionLink(accession) {
        /* RefSeq http://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole */
        if (accession.match(/^[ANYXZ][A-Z]_/)) {
            return 'http://www.ncbi.nlm.nih.gov/nuccore/' + accession;
        }
        /* UTRdb locus */
        if (accession.match(/^[35]HSA/)) {
            return 'http://utrdb.ba.itb.cnr.it/getutr/' + accession + '/1';
        }

        return false;
    }

	jQuery.scoreTable = function (table, task) {

		/* Hook to GFF/Score results only. */
		if (!table.hasClass('result_gff') && !table.hasClass('result_score')) {
		    return;
		}

		/* Create histogram and partition charts. */
		createScoreCharts(table, task.fields, task.result);

        /* Make RefSeq/Locus clickable. */
		table.find("tr").each(function () {
		    var cell = $(this).find('td:first-child');
		    var accession = cell.text();
		    var link = accessionLink(cell.text());
		    if (link) {
		        cell.empty();
		        cell.append('<a href="' + link + '" target="_blank">' + accession + '</a>');
		    }
		});
	}
});


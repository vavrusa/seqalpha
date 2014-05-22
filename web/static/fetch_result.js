var ROW_LIMIT = 50;

$(function () {

	$('a.result_show').bind('click', function() {

		var parent = $(this).parent().parent();
		var load_result = !parent.hasClass('active_result');

		/* Hide all current result tables. */
        $('.result').removeClass('active_result');
        $('a.result_show').text('Show');
        $('#result').empty();
		$('#result').hide();

		/* Return if we're not going to show a result. */
		if (!load_result) {
		    return;
		}

        /* Load current result. */
		$.getJSON($SCRIPT_ROOT + '/_result', { uuid: parent.data('uuid') }, function(data) {

			var task = data.task;
			var subresult = $('<div class="subresult"><h4>Query results in table</h4></div>');

			/* Hook the results table in the container. */
			$('#result').empty();
			$('#result').appendTo(parent);
			$('#result').append(subresult);

			/* Check empty result. */
			if (task.result.length == 0) {
                subresult.append('<div class="centered">No results, try something else.</div>');
                return;
			}

            var table = $('<table class="' + task.type + '"></table');
			subresult.append(table);

            /* Create table heading. */
			var heading = $('<tr />');
			for(i in task.fields) {
				heading.append($('<th>' + task.fields[i] + '</th>'));
			}
			table.append(heading);

            /* Create table data. */
			for(i in task.result) {
				var row = $('<tr />');
				row.data('result_id', i);
				for (k in task.fields) {
					row.append('<td>' + task.result[i][k] + '</td>');
				}
				table.append(row);
				if (i == ROW_LIMIT) {
				    var msg = 'Dataset too large, displaying first 100 results...';
					table.append('<tr><th class="terminator" colspan="' + task.fields.length + '">' + msg + '</td></tr>');
					break;
				}
			}

            /* FASTA table visualization. */
            jQuery.fastaTable(table, task);

            /* Score results table. */
			jQuery.scoreTable(table, task);

			/* GQ topology. */
			jQuery.topologyTable(table, task);
		});

        /* Mark this result as currently visible. */
        parent.addClass('active_result');
		$(this).text('Hide');
		$('#result').show();
		$('#dataset_picker').change();
		return false;
	});

    $('a.result_del').bind('click', function() {

        var parent = $(this).parent().parent();
	    $.getJSON($SCRIPT_ROOT + '/_remove', { uuid: parent.data('uuid') });
        $('#result').empty();
		$('#result').hide();
		$('#result').appendTo('.result_list');
		$('#dataset_picker').change();
		parent.remove();

        /* Rebase the search. */
        var form_uuid = $('#step_runnable input[name="uuid"]');
		form_uuid.val($('.result:first').data('uuid'));

		/* Last step deleted, reset. */
        if ($('.result').length == 0) {
            window.location = $('a#search_reset').attr('href');
        }

    });

	$('a.result_show:first').click();

	/* Search list control. */
	$('a.search_persist').bind('click', function() {

        var parent = $(this).parent();
	    $.getJSON($SCRIPT_ROOT + '/_persist', { uuid: parent.data('uuid'), state: 1 });
	    $(this).html('&#x2713; Search saved');
        $(this).contents().unwrap();

        return false;
    });

	$('a.search_remove').bind('click', function() {

        var parent = $(this).parent().parent();
	    $.getJSON($SCRIPT_ROOT + '/_persist', { uuid: parent.data('uuid'), state: 0 });
	    parent.remove();
	    return false;
    });

});

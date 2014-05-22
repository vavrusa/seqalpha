$(function () {

    function getImage(name) {
        var img_base = $SCRIPT_ROOT + '/static/quadclass/';
        return '<img src="' + img_base + name + '.png" />';
    }

    function topologyReason(reason, arg, pval) {
		var ret = reason + ' is ' + arg;
        switch (reason) {
        case 'length_match': /* Loop length configuration. */
            ret = 'L<sub>1</sub>-L<sub>3</sub> length configuration <b>' + arg + '</b> seen in this GQ family.';
			break;
        case 'length_dt': /* Loop length sequence derivation. */
            ret = 'L<sub>1</sub>-L<sub>3</sub> length sequence derivation <b>' + arg + '</b> seen in this GQ family.';
			break;
        case 'composition': /* Sequence similarity. */
            ret = 'Loops nucleotide composition <b>' + arg + '</b>';
			break;
        }

		ret += ' <i>( P-value = ' + pval + ' )</i>';

		return ret;
    }

    function topologyExplanation(container, result, reasons) {
            container.append('<h5>Hmm... this topology prediction is based on the following evidence:</h5>');
            var list = $('<ol />');
            for (var i in reasons) {
                var pair = reasons[i].split(':');
                list.append('<li>' + topologyReason(pair[0], pair[1], pair[2]) + '</li>');
            }
            container.append(list);

            container.append('<h5>Notes on topology:</h5>');
            container.append('<div>' + result['description'] + '</div>');
    }

    function topologyInfo(index, topo, name, reasons) {
        var subresult = $('<div class="subresult"></div>');

        // Get more info about GQ class
    	$.getJSON($SCRIPT_ROOT + '/_call',
		{ runner: 'quadclass', method: 'get_info', param: [topo, name] },
		function(data) {
		  var result = data.result;
		  subresult.append('<h4>Possible topology #' + index + ': ' + result['name'] + '</h4>');

          var mainbar = $('<div class="mainbar" />');
          topologyExplanation(mainbar, result, reasons);

          var sidebar = $('<div class="sidebar" />');
          var img = $(getImage(result['image'].substr(0, 3)));
          img.addClass('topo_path');
          sidebar.append(img);

          subresult.append(sidebar);
          subresult.append(mainbar);
		});

        return subresult;
    }

    function topologyDetail() {
        $(this).find('td:last-child').each(function() {

            /* Close if previously expanded. */
            var parent = $(this).parent();
            var next = parent.next();
            if (next.attr('id') == 'topology') {
                next.remove();
                return;
            }

            // Parse topology from last cell and create visualization
            var cols = parent.children().length;
            var container = $('<tr id="topology"><td colspan="' + cols + '"></td></tr>');
            var topology = container.find('td');
            topology.append('<p>Here is a breakdown of possible G-quadruplex conformations:</p>');

            var prescript = $(this).data('topo').split(' ');
            for (var i in prescript) {
                var match_str = prescript[i].split('/');
                var topo_type = match_str[0].split(':');
                var reasons = match_str[1].split(',');

                var node = topologyInfo(i, topo_type[0], topo_type[1], reasons);
                topology.append(node);
            }

            // Close previous topology window and reinsert
            $('#topology').remove();
            parent.after(container);
        });

    }

	jQuery.topologyTable = function topologyTable(table, task) {

	    // This function detects 'Topology' column in the table and makes rows with predicted topology clickable.
		if (table.find('th:contains("Topology")').length > 0) {

		    /* Make each such row actionable. */
		    table.find("tr").each(function () {

		        var cell = $(this).find('td:last-child');
		        if (cell.text().length) {
		            $(this).click(topologyDetail);
		            $(this).addClass('clickable');

                    /* Possible topologies array. */
                    cell.data('topo', cell.text());
                    cell.empty();

                    /* Prettify topology names. */
                    var prescript = cell.data('topo').split(' ');
                    for (var i in prescript) {
                        /* Extract topology:name */
                        var topo = prescript[i].split('/')[0].split(':');
                        var container = $('<span style="display: inline-block; margin-right: 1.2em;"/>');
                        cell.append(container);

                        /* Add icons. */
                        for (var k in topo[0]) {
                            container.append(getImage(topo[0][k].toLowerCase()));
                        }

                        container.append('<i>(' + topo[1] + ')</i>');
                    }
		        }
		    }
		    );
		}
	}
});

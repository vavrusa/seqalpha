$(function () {
	$('#dataset_picker').change(function() {
		var dataset = $(this).find('option:selected').val();
		if (dataset == null) {
			dataset = $('.active_result > .result_header:nth-child(2)').text();
		}

		var dataset_type = dataset.slice(dataset.lastIndexOf('.') + 1);
		$('#runner_picker li').each(function() {
			var accepts = $(this).data('accepts');
			$(this).removeClass('disabled');
			if (accepts != '*' && accepts != dataset_type) {
				$(this).addClass('disabled');
			}
		});
		$('#step_param').hide();
	});

	$('#runner_picker').selectable({
		selected: function(event, ui) {
			$('#runner_data').val($(ui.selected).data('id'));
			if ($(ui.selected).hasClass('.disabled')) {
				return;
			}

			var param_type = $(ui.selected).data('param');
			if (param_type) {
                param_type = param_type.replace(/'/g, '"');
                $('#query_input').empty();
                var data = JSON.parse(param_type);
                for(var key in data) {
                    var key_arg = data[key].split('|');
                    var label = $('<label>' + key + '</label>');
                    var input = $('<input type="' + key_arg[0] + '" name="' + key_arg[1] + '" />');
                    input.attr('placeholder', key);
                    if (key_arg.length > 2) {
                        input.attr('value', key_arg[2]);
                    }
                    $('#query_input').append(label);
                    $('#query_input').append(input);
                }
				$('#query_input').show();
			} else {
				$('#query_input').hide();
			}
			$('#step_param').show();
		}
	});

	$('#upload_show').click(function () {
	    var form = $('#upload_form');
	    if (form.hasClass('hidden')) {
	        form.removeClass('hidden');
	    } else {
	        form.addClass('hidden');
	    }
	});

	$('#step_param').hide();
	$('#dataset_picker').change();
});

/* Table initialisation */
$(document).ready(function() {
	$('#allrequestTable').dataTable( {
		"sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
		"sPaginationType": "bootstrap",
		"aaSorting": [[ 1, "desc" ]], // 2nd column sort on #
		"aoColumnDefs": [
      		{ "bSortable": false, "aTargets": [ 0 ] }
    	],
		"iDisplayLength": 50,
		"oLanguage": {
			"sLengthMenu": "_MENU_ records per page"
		}
	} );
	/* adds placeholder text for search box */
	$('.dataTables_filter label input').attr( {
		"placeholder": "I'd like to find...",
		// "class": "text-right",
		});
} );
/* banner dismissal */
$(function(){$(".alert").alert()})


/* navbar active page indicator */
$(function(){
  function stripTrailingSlash(str) {
    if(str.substr(-1) == '/') {
      return str.substr(0, str.length - 1);
    }
    return str;
  }

  var url = window.location.pathname;  
  var activePage = stripTrailingSlash(url);

  $('.nav li a').each(function(){  
    var currentPage = stripTrailingSlash($(this).attr('href'));

    if (activePage == currentPage) {
      $(this).parent().addClass('active'); 
    } 
  });
});

// $(document).ready(function () {
// 	$('.nav li').click(function() {
// 		$('.nav li:active').removeClass('active');
// 	 $('this').addClass('active');
// 	});
// });

/* form in reroute popover */
$('#reroutePopover').popover({ 
    html : true,
    title: function() {
      return $("#reroutePopover-head").html();
    },
    content: function() {
      return $("#reroutePopover-content").html();
    }
});

/* need to include a way to close the popover by clicking anywhere outside the popover - 
currently have to click on button */
// $('rel["clickover"]').clickover();

/* table sort */
$(document).ready(function(){
    $('#allrequestTable').dataTable();
});

	

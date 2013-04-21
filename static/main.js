/* banner dismissal */
$(function(){$(".alert").alert()})


/* navbar active page indicator */

// $(document).ready(function () {
// 	$('.nav li').click(function() {
// 		$('.nav li:active').removeClass('active');
// 	 $('this').addClass('active');
// 	});
// });

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

/* form in reroute popover */
$('#popover').popover({ 
    html : true,
    title: function() {
      return $("#popover-head").html();
    },
    content: function() {
      return $("#popover-content").html();
    }
});

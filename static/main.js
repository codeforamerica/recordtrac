/* banner dismissal */
$(function(){$(".alert").alert()})

// $(document).ready(function () {
// 	$('.nav li').click(function() {
// 		$('.nav li:active').removeClass('active');
// 	 $('this').addClass('active');
// 	});
// });


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

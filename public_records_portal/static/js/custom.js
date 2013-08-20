
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
  // to close the popover
  $('.popover-container').on('click', '.close', function(){
    $('#reroutePopover').popover('hide');
  })


  /* form in history popover */
  $('.historyPopover').popover({
      trigger: 'hover', 
      html : true,
      title: function() {
        return $("#historyPopover-head").html();
      },
      content: function() {
        return $("#historyPopover-content").html();
      }
  });

function directoryPopover(staffName, staffDept, staffPhone, elemID){
        if (!staffPhone) {
        staffPhone = 'Not available';
      }
   /* all popovers */
  $(elemID).popover({
      trigger: 'hover', 
      html : true,
      title: function() {
        return $("Contact information");
      },
      content: function() {
            var $cont = $("<p class='tight_paragraph'><span class='muted'>Department: </span>"+staffDept+"</p><p class='tight_paragraph'><span class='muted'>Email: </span>"+staffName+"</p><p class='tight_paragraph'><span class='muted'>Phone: </span>"+staffPhone+"</p>");
            return $cont;
      }
  });
}


/* tooptip */
  $('[rel=tooltip]').tooltip({html:true}) 

/* need to include a way to close the popover by clicking anywhere outside the popover - 
currently have to click on button */
  // $('rel["clickover"]').clickover();

/* table sort */
// $(document).ready(function() {
//   $('#allrequestTable').dataTable();
// } );

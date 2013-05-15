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

/* submit disable and enable on valid form entry */
  // $(document).ready(function () {
  // 	$('.nav li').click(function() {
  // 		$('.nav li:active').removeClass('active');
  // 	 $('this').addClass('active');
  // 	});
  // });
  // $(document).ready(function () {
  //  $('inputUrl:valid').keyup(function() {
  //    // $('inputUrl:valid').removeClass('disabled');
  //   $('addalink').removeClass('disabled');
  //  });
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

  /* form in history popover */
  $('#historyPopover').popover({ 
      html : true,
      title: function() {
        return $("#historyPopover-head").html();
      },
      content: function() {
        return $("#historyPopover-content").html();
      }
  });

/* tooptip */
  $('[rel=tooltip]').tooltip({html:true}) 

/* need to include a way to close the popover by clicking anywhere outside the popover - 
currently have to click on button */
  // $('rel["clickover"]').clickover();

/* table sort */
  // $(document).ready(function(){
  //     $('#allrequestTable').dataTable();
  // });

  $(document).ready(function() {
    $('#allrequestTable').dataTable( {
        "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>"
    } );
  } );

  // $.extend( $.fn.dataTableExt.oStdClasses, {
  //   "sWrapper": "dataTables_wrapper form-inline"
  // } );

  
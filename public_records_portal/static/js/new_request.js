$(document).ready(function(){
  /* help text popover */
    $('#request_text').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#requestTextPopover-content").html();
        }
    });

    $('#request_email').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#emailPopover-content").html();
        }
    });

    $('#request_name').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#namePopover-content").html();
        }
    });

    $('#request_phone').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#phonePopover-content").html();
        }
    });

    $('#request_address_street').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#streetPopover-content").html();
        }
    });

    $('#request_address_city').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#cityPopover-content").html();
        }
    });

    $('#request_address_zip').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#zipPopover-content").html();
        }
    });


/* End of .ready functionality */


$('#requestTextarea').on('blur', function() {
    request_text = $(this).val();
    request = $.ajax({
      url: '/is_public_record',
      type: 'post',
      data: {
        request_text: request_text
      }
    });
    request.done( function(data) {
      $div = $('#not_public_record');
      if (data != '') {
        $div.addClass('alert').addClass('alert-error');
        $div.html(data);
        $div.prepend("<i class='icon-exclamation-sign'></i> ");
      } else {
        $div.empty();
        $div.removeClass('alert').removeClass('alert-error');
      }
    });
  })
});


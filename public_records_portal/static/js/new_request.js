$(document).ready(function(){

  /* validates add a request form */
  $("#submitRequest").validate({
      rules: {
        request_text: {
          required: true,
          minlength: 2
        }
      },
      highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
      },
      success: function(element) {
        element
          .closest('.control-group').removeClass('error').addClass('success');
      }
    });


  /* help text popover */
    $('#requestTextarea').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#requestPopover-content").html();
        }
    });

    $('#inputEmail').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#emailPopover-content").html();
        }
    });

    $('#inputName').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#namePopover-content").html();
        }
    });

    $('#inputPhone').popover({
        trigger: 'focus',
        html : true,
        content: function() {
          return $("#phonePopover-content").html();
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


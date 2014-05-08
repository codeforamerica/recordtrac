/* add a request form found at /new */
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

  /* 
  typeahead for department that is now a dropdown as well using combobox:
  https://github.com/danielfarrell/bootstrap-combobox/
  */

  /* First entry is an empty one */
 $('#inputDepartment').append($("<option/>", {
              value: '',
              text: ''
          }));
 /* Initialize the select element with data from doctypes.json */
  $.getJSON("static/json/doctypes.json", function(data) {
      $.each(data, function (i, line) {
        var department = line['DEPARTMENT'];
        var doc_type = line['DOC_TYPE'];
          $('#inputDepartment').append($("<option/>", {
              value: department,
              text: department + " - " + doc_type
          }));

  });
  /* Initialize the combobox */
  $('.combobox').combobox(); 


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
/* End of .blur functionality */
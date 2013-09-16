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
  var map = {};
  var departments = [];
  var doc_types = [];
  var output = [];
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
        if($.inArray(department, departments) == -1) {
          departments.push(department);
         }
          map[doc_type + " - " + department] = department;
          $('#inputDepartment').append($("<option/>", {
              value: department,
              text: doc_type + " - " + department
          }));
          doc_types.push(doc_type + " - " + department);

  });
  /* Initialize the combobox */
  $('.combobox').combobox(); 

});
/* End of .ready funcitonality */


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
  /* validates add a request form */
  $(document).ready(function(){

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
        .closest('.control-group').removeClass('error').addClass('success');
        }
    });

  });

$(document).ready(function() {
var map = {};
var departments = [];
var doc_types = [];
$.getJSON("static/json/doctypes.json", function(data) {
      $.each(data, function (i, line) {
        var department = line['DEPARTMENT'];
        var doc_type = line['DOC_TYPE'];
        if($.inArray(department, departments) == -1) {
          departments.push(department);
         }
          map[doc_type + " - " + department] = department;
          doc_types.push(doc_type + " - " + department);
       });
    });
/* typeahead for email in reroute form */
$('#inputDepartment').typeahead({
      source: doc_types
      , updater: function (item) {
        department = map[item];
        return department;
      }
      ,matcher: function(item) {
        if (item.toLowerCase().indexOf(this.query.trim().toLowerCase()) != -1){
        return true;
       }
      }
    , items: 8
    , menu: '<ul class="typeahead dropdown-menu"></ul>'
    , item: '<li><a href="#"></a></li>'
    , minLength: 1
    })

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

  /* validates add a request form */
  $(document).ready(function(){

    $("#submitRequest").validate({
      // ignore: ".ignore",
      rules: {
        request_text: {
          required: true,
          minlength: 2
             }
         },
      highlight: function(element) {
          // $('#inputEmail').addClass('ignore');
          // $('#requestButton').html(
          //   "<div id='no_email' class='alert alert-block alert-error fade in'>"+
          //     "<h4 class='alert-heading'>Oops, you forgot to provide an email address.</h4>"+
          //       "<p>Your email is how we contact you.  If you choose to leave it blank, you will not receive updates about your request.  Your request may take longer or be dismissed if it is missing important information. You can still enter your e-mail address at this time, and continue with submission.</p>"+
          //       "<button id='submit_anyway' class='btn btn-danger' type='submit'>Got it, submit my request!</button>"+
          //     "</div>"
          //   );
        $(element).closest('.control-group').removeClass('success').addClass('error');
        },
      success: function(element) {
        // $('#requestButton').html(
        //   "<div id='requestButton' class='control-group'>"+
        //     "<div class='controls'>"+
        //       "<button type='submit' class='btn btn-large btn-primary'>Request</button>"+
        //     "</div>"+
        //   "</div>"
        //   );
        element
        .text('OK!').addClass('valid')
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
      $('#not_public_record').html(data);
    });
  })
});

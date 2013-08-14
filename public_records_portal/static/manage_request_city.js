$(document).ready(function(){
  /* validates add a record form */
  $("#submitRecord").validate({
    rules: {
      record_description: {
        required: true,
        minlength: 2
           }
       },
     highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
      },
      success: function(element) {
        element
        .text('OK!').addClass('valid')
        .closest('.control-group').removeClass('error').addClass('success');
      }
  });

  /* validates extension form */
  $("#extension").validate({
    rules: {
      extend_reasons: {
        required: true
           }
       },
     highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
      },
      success: function(element) {
        element
        .text('OK!').addClass('valid')
        .closest('.control-group').removeClass('error').addClass('success');
      }
  });
});

  /* takes text from json file for each reason and populates the editable textarea in the modal */
  $("#close_reasons").change(function () {
    var str = "";
    $("#close_reasons option:selected").each(function () {
          str += $(this).val() + " ";
        });
    $("#closeTextarea").text(str);
  });

  /* takes the edited text in the modal as a variable for use in posting to the case */
  $("#closeButton").click(function () {
    var estr = $("#closeTextarea").val();
    $('input[name=close_reason]').val(estr);
  });

var map = {};
var emails = []

$(document).ready(function() {
  /* typeahead for email in reroute form */
  $('#rerouteEmail').typeahead.defaults = {
      source: function(query, process) {
        var contacts = [];
        $.getJSON("{{ url_for('static', filename='directory.json') }}", function(data) {
            $.each(data, function (i, line) {
              var array = line['FULL_NAME'].split(",");
              var first = array[1];
              var last = array[0];
              emails.push(line.EMAIL_ADDRESS);
              map[first + " " + last + " - " + line.EMAIL_ADDRESS] = line.EMAIL_ADDRESS;
              contacts.push(first + " " + last + " - " + line.EMAIL_ADDRESS);
         });
         process(contacts);
        });
      }
      , updater: function (item) {
        selectedContact = map[item];
        return selectedContact;
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
    }
});
$(document).on('shown', "#reroutePopover", function () {
   $('#rerouteButton').click(function() {
    if($.inArray($('#rerouteEmail').val(), emails) == -1) {
      $('#rerouteEmail').val('');
    }
  });
});

$(document).ready(function() {
  (function( $ ){
    $.fn.sticky = function() {
      
        // Do your awesome plugin stuff here

    };
  })( jQuery );


  $('[data-sticky]').sticky();
})

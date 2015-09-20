/* add a request form found at /new */
$(document).ready(function(){
  /* validates track request form */
  $("#submitTrack").validate({
      rules: {
        request_id: {
          required: true,
         },
      highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
        },
      success: function(element) {
        element
        .closest('.control-group').removeClass('error').addClass('success');
        }
      },
    });
 });
$(document).ready(function(){
  /* validates ask a question form */
  $("#question").validate({
    rules: {
      question_text: {
        required: true,
        minlength: 2
           }
       },
     highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
      },
      success: function(element) {
        element
        // .text('OK!').addClass('valid')
        .closest('.control-group').removeClass('error').addClass('success');
      }
  });

  /* validates add a record form */
  $("#submitRecord").validate({
    rules: {
      record_description: {
        required: true,
        minlength: 2,
        maxlength: 40
           }
       },
     highlight: function(element) {
        $(element).closest('.control-group').removeClass('success').addClass('error');
      },
      success: function(element) {
        element
        // .text('OK!').addClass('valid')
        .closest('.control-group').removeClass('error').addClass('success');
      }
  });

  /* validates add a note form */
  $("#note").validate({
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
        // .text('OK!').addClass('valid')
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

  /* validates new PoC form */
  $("#rerouteForm").validate({
    rules: {
      owner_reason: {
        required: true
           },
      owner_email: {
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

  /* validates new Helper form */
  $("#notifyForm").validate({
    rules: {
      owner_reason: {
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

  /* validates remove Helper form */
  $("#unassignForm").validate({
    rules: {
      reason_unassigned: {
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




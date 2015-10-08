// $(document).ready(function(){
//   /* validates ask a question form */
//   $("#question").validate({
//     rules: {
//       question_text: {
//         required: true,
//         minlength: 2
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         // .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates add a record form */
//   $("#submitRecord").validate({
//     rules: {
//       record_description: {
//         required: true,
//         minlength: 2,
//         maxlength: 40
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         // .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates add a note form */
//   $("#note").validate({
//     rules: {
//       record_description: {
//         required: true,
//         minlength: 2
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         // .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates extension form */
//   $("#extension").validate({
//     rules: {
//       extend_reasons: {
//         required: true
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates new PoC form */
//   $("#rerouteForm").validate({
//     rules: {
//       owner_reason: {
//         required: true
//            },
//       owner_email: {
//         required: true
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates new Helper form */
//   $("#notifyForm").validate({
//     rules: {
//       owner_reason: {
//         required: true
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });

//   /* validates remove Helper form */
//   $("#unassignForm").validate({
//     rules: {
//       reason_unassigned: {
//         required: true
//            }
//        },
//      highlight: function(element) {
//         $(element).closest('.control-group').removeClass('success').addClass('error');
//       },
//       success: function(element) {
//         element
//         .text('OK!').addClass('valid')
//         .closest('.control-group').removeClass('error').addClass('success');
//       }
//   });
  
// });

$(document).ready(function() {


  (function( $ ){
    $.fn.sticky = function() {

        // Do your awesome plugin stuff here

    };
    $.fn.truncateable = function() {
      $self = $(this)
      var text = $self.text().trim();
      var current_length = text.length;
      var max_length = $self.attr('truncateable');
      if (current_length < max_length)
        return;
      var truncated = text.substring(0, max_length);
      var fullhtml = $self.html();

      $self.html("<div class='truncated-text' truncated='"+truncated+"'>"+truncated+"</div>");
      $self.append("<div class='more'>..more</div>");
      $self.attr('full-text', fullhtml);
    };
  })( jQuery );

  $('[data-sticky]').sticky();
  $('[truncateable]').each(function(){
    $this = $(this);
    $this.truncateable();
  });
  $('[truncateable]').on('click','.more', function(e){
    var $parent = $(e.delegateTarget);
    var full_text = $parent.attr('full-text');
    $parent.find('.truncated-text').html(full_text);
    $(this).remove();
    $parent.append(("<div class='less'>...less</div>"))
  });
  $('[truncateable]').on('click','.less', function(e){
    var $parent = $(e.delegateTarget);
    $truncated_div = $parent.find('.truncated-text');
    $truncated_div.html($truncated_div.attr('truncated'));
    $(this).remove();
    $parent.append("<div class='more'>..more</div>");
  });

})



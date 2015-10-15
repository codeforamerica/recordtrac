(function(){

  $('#load-more-qa').on('click', function() {
    $.getJSON('/api/request/2', function(data) {
      var html = '';
      var qas = data.qas;
      for (var i = 0; i < qas.length; i++) {
        var qa = qas[i];
        html += qa_to_html(qa);
      }
      $('#load-more-qa').before(html);
    });
  });

  function qa_to_html (qa) {
    return '<h3>' + qa.date_created+ '</h3>';
  }

  // hide/show responses
  var $responses = $('.response');
  hideExcept([0], $responses);

  // hides elements, can take a whitelist of indexes
  // ex: to hide all but first ->
  //    hideExcept([0], $elem);
  function hideExcept(whitelist, elem) {
    $.each(elem,
      function(i, el) {
        if ($.inArray(i,whitelist) == -1) {
            $(el).hide();
        }
      });
  }

  $('.case-show-all').on('click',function() {
    var $this = $(this);
    if ($(this).hasClass('show')) {
      $this.toggleClass('show');
      $responses.show(200);
      $this.html('<i class="icon-chevron-up"></i> See less <i class="icon-chevron-up"></i>')
    } else {
      $this.toggleClass('show');
      hideExcept([0], $responses);
      $this.html('<i class="icon-chevron-down"></i> See all <i class="icon-chevron-down"></i>')
    }
  });
  $('#acknowledgeRequestForm').on('click',function() {
      if ($('#acknowledgeRequestForm').css('display') != 'none') {
        $('#acknowledgeRequestForm').hide();
      }
  });
 
  $("#days_after").change(function() {
    selected = $(this).val();
    if(selected === "0") { 
      $("#custom_due_date").show();
      }
    else {
      $("#custom_due_date").hide();
    }
});


  $("#days_after").change(function() {
    selected = $(this).val();
    if(selected === "-1") { 
      $("#custom_due_date").show();
    }
    else {
      $("#custom_due_date").hide();
    }
  });

  $('#askQuestion').on('click',function(){
    $('#modalQuestionTable').show();
    $('#question_text').html($('#questionTextarea').val());
  });

  $('#submit').on('click',function(){
    additional_information = $('#additional_note').val();
    form_id = '#' + $('#form_id').val();
    var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "additional_information").val(additional_information);
    $(form_id).append($(input));
    $(form_id).submit();
   });

  $('#rerouteButton').on('click',function(){
    $('#form_id').val('note');
    var modalQuestion = 'Are you sure you want to acknowledge the request for the number of days below and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#acknowledge_status').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#extendButton').on('click',function(){
    $('#form_id').val('extension');
    days = $('#days_after').val();
    var modalQuestion = 'Are you sure you want to request an extension for the number of days below and send an email to the requester?';

    if (days != -1) {
        modalQuestion += '<br><br>' + $('#days_after').val() + " days";
     }
     else {
        due_date = $('#due_date').val();
        year = due_date.substring(0,4);
        month = due_date.substring(5,7);
        day = due_date.substring(8,10);
        modalQuestion = 'Are you sure you want to set the following due date and send an email to the requester?';
        modalQuestion += '<br><br>' + month + "/" + day + "/" + year;
     }
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#closeButton').on('click',function(){
    $('#form_id').val('closeRequest');
    var modalQuestion = 'Are you sure you want to close the request for the reasons below and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#close_reasons').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#addRecordButton').on('click',function(){
    $('#form_id').val('submitRecord');
    var modalQuestion = 'Are you sure you want to add this record and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#recordSummary').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#addNoteButton').on('click',function(){
    $('#form_id').val('note');
    var modalQuestion = 'Are you sure you want to add the note below and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#noteTextarea').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#notifyButton').on('click',function(){
    $('#form_id').val('notifyForm');
    var modalQuestion = 'Are you sure you want to add the helper and send an email to the requester? Please specify the reason below.';
    modalQuestion += '<br><br>' + $('#notifyReason').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });



})($);

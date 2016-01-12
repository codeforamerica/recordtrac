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
    $('#modalAdditionalInfoTable').show();
    $('#modalQuestionTable').show();
    $('#question_text').html($('#questionTextarea').val());
  });

  $('#submit').on('click',function(event){
    form_id = '#' + $('#form_id').val();
    if(!$('#modalAdditionalInfoTable').is(':visible') || $(form_id) == 'note_pdf') {
        $('#confirm-submit').modal('toggle');
        $(form_id).submit();
    }
    else {

      $('#modalAdditionalInfoTable').show();
      additional_information = $('#additional_note').val();
      var input = $("<input>")
               .attr("type", "hidden")
               .attr("name", "additional_information").val(additional_information);
      $(form_id).append($(input));
      $(form_id).submit();
    }
   });

    $('#cancel_close').on('click',function(event){
        $('#close-reminder').hide();
    });

  $('#rerouteButton').on('click',function(){
    $('#form_id').val('AcknowledgeNote');
    var modalQuestion = 'Are you sure you want to acknowledge the request for the number of days below and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#acknowledge_status').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#extendButton').on('click',function(){
    $('#modalAdditionalInfoTable').show();
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
    $('#modalAdditionalInfoTable').show();
    $('#close-reminder').show()
    //$('#modalAdditionalInfoTable').append('<p><b>If you are denying this request please explain why.</b></p>');
    $('#form_id').val('closeRequest');
    var modalQuestion = 'Are you sure you want to close the request for the reasons below and send an email to the requester?';
    var reasons = $('#close_reasons').val();
    modalQuestion += '<br><br>';
    var i;
    for (i = 0 ; i < reasons.length ; i++){
        modalQuestion += '<br><br>' + reasons[i];
    }
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();

  });


$('#file_upload_filenames').bind('DOMNodeInserted', function(event) {
  var names = [];
  for (var i = 0; i < $("input[name=record]").get(0).files.length; ++i) {
    names.push($("input[name=record]").get(0).files[i].name);
  }

  $('#file_upload_one').text(names[0]);
  $('#file_upload_two').text(names[1]);
  $('#file_upload_three').text(names[2]);
  $('#file_upload_four').text(names[3]);
  
});

$('#close_filenames_list').on('click',function(){ 
  $('#file_upload_one').empty();
  $('#file_upload_two').empty();
  $('#file_upload_three').empty();
  $('#file_upload_four').empty();
});

  $('#addRecordButton').on('click',function(){
    $('#modalAdditionalInfoTable').show();
    $('#form_id').val('submitRecord');
    var modalQuestion = 'Are you sure you want to add this record and send an email to the requester?';
    modalQuestion += $('#recordSummary').text();
    $('#modalquestionDiv').text(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $('#addNoteButton').on('click',function(){
    $('#modalAdditionalInfoTable').show();
    $('#form_id').val('note');
    var modalQuestion = 'Are you sure you want to add the note below and send an email to the requester?';
    modalQuestion += '<br><br>' + $('#noteTextarea').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

   $('#addPublicNoteButton').on('click', function () {
      $('#modalAdditionalInfoTable').hide();
      $('#form_id').val('note');
      var modalQuestion = 'Are you sure you want to add the note below to this request?';
      modalQuestion += '<br><br>' + $('#noteTextarea').val();
      $('#modalquestionDiv').html(modalQuestion);
      $('#modalQuestionTable').hide();
    });
 
  $('#generatePDFButton').on('click',function(event){
    var selectedTemplate = $('#response_template option:selected').text();
    var modalQuestion = 'Are you sure you want to generate a Word Document for the template below?';
           
    if (selectedTemplate === '') {
      $('#missing_pdf_template').removeClass('hidden');
    }
    else {
        $('#missing_pdf_template').addClass('hidden');
        var attr = $('#generatePDFButton').attr('data-toggle');
        $('#generatePDFButton').attr('data-toggle','modal');
        $('#generatePDFButton').attr('data-target','#confirm-submit');
                             
        $('#modalAdditionalInfoTable').hide();
        $('#form_id').val('note_pdf');
        modalQuestion += '<br><br>' + selectedTemplate;
        $('#modalquestionDiv').html(modalQuestion);
        $('#modalQuestionTable').hide();
    }
                            
        
        
  });

  $('#notifyButton').on('click',function(){
    $('#form_id').val('notifyForm');
    var modalQuestion = 'Are you sure you want to add the helper and send an email to the requester? Please specify the reason below.';
    modalQuestion += '<br><br>' + $('#notifyReason').val();
    $('#modalquestionDiv').html(modalQuestion);
    $('#modalQuestionTable').hide();
  });

  $("#requesterInfoButton").on('click', function() {
    $('#requester_info').toggle();
    $('#requesterInfoButton').innerHTML()
  });

$(document).on('ready', function() {
    $("#record").fileinput({
        maxFileCount: 4,
    validateInitialCount: true,
    overwriteInitial: false,
    allowedFileExtensions: ["txt", "pdf", "doc", "rtf", "odt", "odp", "ods", "odg","odf","ppt", "pps", "xls", "docx", "pptx", "ppsx", "xlsx","jpg","jpeg","png","gif","tif","tiff","bmp","avi","flv","wmv","mov","mp4","mp3","wma","wav","ra","mid"]
    });
});
})($);

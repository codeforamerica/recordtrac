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
      alert("TEST");
      if ($('#acknowledgeRequestForm').css('display') != 'none') {
        $('#acknowledgeRequestForm').hide();
      }
    }
  });

})($);

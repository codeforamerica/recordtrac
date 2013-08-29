(function(){

  $('#load-more-qa').on('click', function() {
    $.getJSON('/api/request/2', function(data) {
      var html = '';
      var qas = data.qas;
      for (var i = 0; i < qas.length; i++) {
        var qa = qas[i];
        html += qa_to_html(qa);
        console.log(qa);
      }
      $('#load-more-qa').before(html);
    });
  });

  function qa_to_html (qa) {
    return '<h3>' + qa.date_created+ '</h3>';
  }

})($);

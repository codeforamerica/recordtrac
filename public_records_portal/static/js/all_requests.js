$(document).ready(function(){
    Modernizr.load({
        test: Modernizr.inputtypes.date,
        nope: ['//ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js', '//ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/jquery-ui.min.js','//ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/themes/base/jquery-ui.css'],
          complete: function () {
        $('input[type=date]').datepicker({
      dateFormat: 'yy-mm-dd'
    }); 
  }
});

});

$(document).ready(function(){

  $('#datepicker').datepicker();
  var currentDate = new Date();
  currentDay = (currentDate.getMonth()+1) + '/' + currentDate.getDate() + '/' + currentDate.getFullYear();
  $('#datepicker').val(currentDay);

});
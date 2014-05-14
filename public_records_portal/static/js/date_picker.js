$(document).ready(function(){

  $("input[id^='datepicker']").datepicker();
  var currentDate = new Date();
  currentDay = (currentDate.getMonth()+1) + '/' + currentDate.getDate() + '/' + currentDate.getFullYear();
  $("input[id^='datepicker']").val(currentDay);

});
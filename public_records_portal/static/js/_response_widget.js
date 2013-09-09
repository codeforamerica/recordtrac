(function(){

  var $rw_wrap = $('.rw-container');

  $rw_wrap.on('click', '.rw-btn-wrap', function(e){
    $container = $(e.delegateTarget);
    $this = $(this);
    target = $this.data('target');
    if ($this.hasClass('active')) {
      $this.removeClass('active');
      $container.find('[data-target-for="'+target+'"]').hide('400');
    } else {
      // active tab background transitions
      $container.find('.rw-btn-wrap').each(function(){
        $(this).removeClass('active');
      });
      $this.addClass('active');
      // toggle content (data-target)
      $container.find('[data-target-for]').each(function(){
        $(this).hide();
      });
      $container.find('[data-target-for="'+target+'"]').show('400');
    }
  });


})($);

(function(){
  
  var $rw_wrap = $('.rw-container');
  var $rw_btns_wrap = $rw_wrap.find('.rw-controller-btns-container');
  var $rw_actions_wrap = $rw_wrap.find('.rw-actions-container');

  $rw_btns_wrap.on('click', '.rw-btn', function(){
    $this = $(this);
    target = $this.data('target');
    // active tab background transitions
    $rw_btns_wrap.find('.rw-btn-wrap').each(function(){
      $(this).removeClass('active');
    });
    $this.parent().addClass('active');
    // toggle content (data-target)
    $rw_actions_wrap.find('[data-target-for]').each(function(){
      $(this).hide();
    })
    $rw_actions_wrap.find('[data-target-for="'+target+'"]').show();
  });

})($);

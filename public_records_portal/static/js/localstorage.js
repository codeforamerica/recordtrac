// local storage for new request form

(function ( $ ) {
    $.fn.FormCache = function( options ) {
        var settings = $.extend({
        }, options );
        
        function on_change(event) {
            var input = $(event.target);
            var key = input.parents('form:first').attr('id');
            var data = JSON.parse(localStorage[key]);
            
            if(input.attr('type') == 'radio' || input.attr('type') == 'checkbox') {
                data[input.attr('id')] = input.is(':checked');
            }else {
                data[input.attr('id')] = input.val();
            }
            
            localStorage[key] = JSON.stringify(data);
        }
        
        return this.each(function() {    
            var element = $(this);
            
            if(typeof(Storage)!=="undefined"){
                var key = element.attr('id');
                
                var data = false;
                if(localStorage[key]) {
                    data = JSON.parse(localStorage[key]);
                }
                
                if(!data) {
                    localStorage[key] = JSON.stringify({});
                    data = JSON.parse(localStorage[key]);
                }
                element.find('input, select, textarea').change(on_change);
                
                element.find('input, select, textarea').each(function(){
                    if($(this).attr('type') != 'submit') {
                        var input = $(this);
                        var value = data[input.attr('id')];
                        if(input.attr('type') == 'radio' || input.attr('type') == 'checkbox') {
                            if(value) {
                                input.attr('checked', input.is(':checked'));
                            } else {
                                input.removeAttr('checked');
                            }
                        } else {
                            input.val(value);
                        }
                    }
                });
                
                
            }
            else {
                // alert('local storage is not available');
            }
        });
    };     
}( jQuery ))

$(document).ready(function(){

	// run the plugin on load
    $('form').FormCache();

    // clear local storage once the form has been submitted

    $('#button2').click(function () {
		localStorage.clear();
    });
    
});
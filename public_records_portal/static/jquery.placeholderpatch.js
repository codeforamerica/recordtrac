/*
 * placeholder: a jQuery plugin
 *
 * Licensed under the MIT:
 * http://www.opensource.org/licenses/mit-license.php
 *
 */

(function ($) {
  $.extend($.fn, {
    placeholder: function (options) {
      var defaults = {placeholderClass: 'placeholder'};

      options = $.extend(defaults, options);

      return this.each(function () {
        var input = $(this).addClass(options.placeholderClass);
        var form  = input.parents('form:first');
        var text  = input.val() || input.attr('placeholder');

        if (text) {
          input.val(text);

          input.focus(function () {
            clearInput();
          }).blur(function () {
            unclearInput();
          });

          form.submit(function() {
            if (input.hasClass(options.placeholderClass)) {
              input.val('');
            }
          });

          input.blur();
        }

        function clearInput() {
          if (input.val() === text) {
            input.val('');
          }

          input.removeClass(options.placeholderClass);
        }

        function unclearInput() {
          if (input.val() === '') {
            input.addClass(options.placeholderClass).val(text);
          }
        }
      });
    }
  });
})(jQuery);

jQuery(document).ready(function ($) {
  $('[placeholder]:not([type="password"])').placeholder();
});
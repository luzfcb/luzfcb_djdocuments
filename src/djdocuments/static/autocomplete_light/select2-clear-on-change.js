// ;(function ($) {
//     $(document).on('autocompleteLightInitialize', '[data-autocomplete-light-function=select2]', function () {
//         var element = $(this);
//
//         (function (autocomplete_element) {
//             var forward = $(autocomplete_element).attr('data-autocomplete-light-clear-on-change');
//             if (forward !== undefined) {
//                 forward = forward.split(',');
//
//                 var parts = $(autocomplete_element).attr('name').split('-');
//                 var prefix = '';
//
//                 for (var i in parts) {
//                     var test_prefix = parts.slice(0, i).join('-');
//                     if (!test_prefix.length) continue;
//                     test_prefix += '-';
//
//                     if ($(':input[name=' + test_prefix + forward[0] + ']').length) {
//                         var prefix = test_prefix;
//                     }
//                 }
//
//                 for (var key in forward) {
//                     var name = prefix + forward[key];
//                     var element_selector_str = '[name=' + name + ']';
//                     // attach change event on "forward fields" to clean
//                     // autocomplete_element if "forward field" has changed
//                     $(element_selector_str).on('change', function () {
//                         // this clean current selection on autocomplete field
//                         $(autocomplete_element).empty().trigger('change')
//                     });
//                 }
//             }
//
//         })(element);
//
//     });
//
// })(yl.jQuery);

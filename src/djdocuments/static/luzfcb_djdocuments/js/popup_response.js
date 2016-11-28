/*global opener */
(function() {
    'use strict';
    var initData = JSON.parse(document.getElementById('django-admin-popup-response-constants').dataset.popupResponse);
    switch(initData.action) {
    case 'change':
        opener.dismissChangeRelatedObjectPopup(window, initData.value, initData.obj, initData.new_value, initData.other);
        break;
    case 'delete':
        opener.dismissDeleteRelatedObjectPopup(window, initData.value, initData.other);
        break;
    default:
        opener.dismissAddRelatedObjectPopup(window, initData.value, initData.obj, initData.other);
        break;
    }
})();

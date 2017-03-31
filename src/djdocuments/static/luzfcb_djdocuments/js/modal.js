/**
 * Created by luzfcb on 31/03/17.
 */
'use strict';

var botao_abrir_modal = $('.botao-abrir-modal');
var modal_div = $('.minha-modal');
var modal_ized = '';

botao_abrir_modal.on('click', function (event) {
    event.preventDefault();
    console.log('botao_abrir_modal click event');
    var url = $(this).attr('href');

    modal_ized = modal_div.iziModal({
        autoOpen: false,
        restoreDefaultContent: true,
        onOpened: function (modal) {
            $(modal).iziModal('recalculateLayout');
            $(".iziModal-content").find(':input:not(button):enabled:visible:first').focus();

        },
        onClosed: function (modal) {
            // clean the content of modal
            $(".iziModal-content").html('');
        }
    });
    modal_ized.on('opening', function (event) {
        var modal = $(this);
        modal.iziModal('startLoading');
        console.log('onOpening modal: ');
        console.log(modal);
        // modal.startLoading();
        var ajax_request_cfg = {
            url: url,
            cache: false,
            method: "GET"
        };
        var request = $.ajax(ajax_request_cfg);
        request.done(function (data) {
            var response_data = $(data);
            console.log('ajax get done');
            $(".iziModal-content").html(response_data);

        });
        request.fail(function (jqXHR, textStatus) {
            console.log('ajax get fail');
            alert("Request failed: " + textStatus);
        });
        request.always(function (jqXHR, textStatus, errorThrown) {
            // 1.4.2 the method name is recalculateLayout
            // but on 1.5.0 beta, the method was renamed to recalcLayout
            modal.iziModal('stopLoading');
            modal.iziModal('recalculateLayout');

        });

    });
    modal_ized.iziModal('open');

    setTimeout(function () {

        modal_ized.iziModal('close');
        setTimeout(function () {
            modal_ized.iziModal('open');
            console.log('modal_ized: ');
            console.log(modal_ized);

        }, 1000);
    }, 6000);
});

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
    var that = $(this);
    var ajax_running = false;
    var url = that.attr('href');

    that.prop('disabled', true);
    modal_ized = modal_div.iziModal({
        autoOpen: false,
        top: '800px',
        width: '80%',
        restoreDefaultContent: true,
        onOpened: function (modal) {
            // $(modal).iziModal('recalculateLayout');
            $(".iziModal-content", modal).find(':input:not(button):enabled:visible:first').focus();

        },
        onClosed: function (modal) {
            // clean the content of modal
            // $(".iziModal-content").html('');
            $('[data-scriptautoadded]').remove();
        }
    });
    modal_ized.on('opening', function (event) {
        var modal = $(this);
        var star_ajax = false;
        var izi_content = $(".iziModal-content", modal);
        izi_content.on('change', function (event) {
            if(star_ajax === true){

            }
        });
        modal.iziModal('startLoading');
        console.log('onOpening modal: ');
        console.log(modal);
        // modal.startLoading();
        var ajax_request_cfg = {
            url: url,
            cache: false,
            method: "GET"
        };
        ajax_running = true;
        var request = $.ajax(ajax_request_cfg);
        request.done(function (data) {
            var response_data = $('<div>' + data + '</div>');
            var scripts = response_data.find('script').clone();
            var css = response_data.find('link').clone();
            $('script', response_data).remove();
            $('link', response_data).remove();
            response_data = response_data.html();
            scripts.attr('data-scriptautoadded', 'true');
            css.attr('data-scriptautoadded', 'true');
            $('head').append(css);
            $('body').append(scripts);
            izi_content.html(response_data);


        });
        request.fail(function (jqXHR, textStatus) {
            console.log('ajax get fail');
            alert("Request failed: " + textStatus);
        });
        request.always(function (jqXHR, textStatus, errorThrown) {
            // 1.4.2 the method name is recalculateLayout
            // but on 1.5.0 beta, the method was renamed to recalcLayout
            modal.iziModal('stopLoading');
            // modal.iziModal('recalculateLayout');
            that.attr('disabled', false);

        });
        return false;
    });
    modal_ized.load(

    );
    modal_ized.iziModal('open');

    // setTimeout(function () {
    //
    //     modal_ized.iziModal('close');
    //     setTimeout(function () {
    //         modal_ized.iziModal('open');
    //         console.log('modal_ized: ');
    //         console.log(modal_ized);
    //
    //     }, 1000);
    // }, 6000);


});

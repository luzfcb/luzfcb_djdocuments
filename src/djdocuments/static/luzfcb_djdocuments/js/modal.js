/**
 * Created by luzfcb on 31/03/17.
 */
'use strict';

var botao_abrir_modal = $('.botao-abrir-modal');
var modal_div = $('.minha-modal');

botao_abrir_modal.on('click', function (event) {
    event.preventDefault();
    console.log('botao_abrir_modal click event');
    var that = $(this);

    var ajax_running = false;
    var url = that.attr('href');

    that.prop('disabled', true);
    modal_ized.iziModal('open');
    modal_ized.on('opened', function (e) {
        do_ajax(that, url, $(this));
    });

});


var modal_ized = modal_div.iziModal({
    autoOpen: false,
    top: '10%',
    width: '80%',
    restoreDefaultContent: true,
    onOpening: function (modal) {
        modal.startLoading();

    },
    onOpened: function (modal) {
        // $(modal).iziModal('recalculateLayout');
        $(".iziModal-content", modal).find(':input:not(button):enabled:visible:first').focus();

    },
    onClosed: function (modal) {
        // clean the content of modal
        // $(".iziModal-content").html('');
        $('[data-scriptautoadded]').off().remove();
        modal_div.removeClass('bah').addClass('bah');
    }
});

var do_ajax = function (el, url, modal) {
    var star_ajax = false;
    var that = el;
    var izi_content = $(".iziModal-content", modal);
    console.log(modal);
    // modal.startLoading();
    var ajax_request_cfg = {
        url: url,
        cache: false,
        method: "GET"
    };
    var request = $.ajax(ajax_request_cfg);

    request.done(function (data) {
        var response_data = $('<div>' + data + '</div>');
        var scripts = response_data.find('script').clone();
        var css = response_data.find('link').clone();
        $('script', response_data).remove();
        $('link', response_data).remove();
        console.log('tamanho css: ' + css.length);
        console.log('tamanho scripts: ' + scripts.length);

        // executar_apos_carregar([scripts], modal);
        response_data = response_data.html();
        scripts.attr('data-scriptautoadded', 'true');
        css.attr('data-scriptautoadded', 'true');
        $('head').append(css);
        $('body').append(scripts);
        modal_div.removeClass('bah');
        izi_content.html(response_data);
        modal.iziModal('recalcLayout');

        $(window).ready(function () {
            modal.iziModal('stopLoading');
            izi_content.fadeIn();
            console.log("hahah");
        });

    });
    request.fail(function (jqXHR, textStatus) {
        console.log('ajax get fail');
        alert("Request failed: " + textStatus);
    });
    request.always(function (jqXHR, textStatus, errorThrown) {
        // 1.4.2 the method name is recalculateLayout
        // but on 1.5.0 beta, the method was renamed to recalcLayout
        // modal.iziModal('stopLoading');
        // modal.iziModal('recalculateLayout');
        that.attr('disabled', false);

    });

};
var executar_apos_carregar = function (elements_array, modal) {
    var total_itens = 0;
    var els = elements_array;
    if (!Array.isArray(els)) {
        els = [els];
    }

    $(els).each(function (index, obj) {
        total_itens += obj.length;
    });

    $(els).each(function (index, obj) {
        // console.log('obj: ' + $(obj).html());

        $(obj).each(function (index, o) {
            console.log('o: ' + $(o).html());
            o.addEventListener('load', function () {
                console.log('loaded');
            });
            $(o).on('load', function () {
                total_itens -= 1;
                if (total_itens === 0) {
                    modal.iziModal('stopLoading');
                }
                console.log('total_itens: ' + total_itens);
            });
        });
    });
};



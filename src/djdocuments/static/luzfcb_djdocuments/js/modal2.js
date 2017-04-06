/**
 * Created by luzfcb on 31/03/17.
 */
'use strict';

// http://www.accessify.com/tools-and-wizards/developer-tools/html-javascript-convertor/
var modal_template = "";
modal_template += "    <div id=\"myModal\" class=\"modal hide fade\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"myModalLabel\"";
modal_template += "         aria-hidden=\"true\">";
modal_template += "        <div class=\"modal-header\">";
modal_template += "            <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">×<\/button>";
modal_template += "            <h3 id=\"myModalLabel\">Modal header<\/h3>";
modal_template += "        <\/div>";
modal_template += "        <div class=\"modal-body\">";
modal_template += "";
modal_template += "        <\/div>";
modal_template += "        <div class=\"modal-footer\">";
modal_template += "";
modal_template += "        <\/div>";
modal_template += "    <\/div>";


var botao_abrir_modal = $('.botao-abrir-modal');
var modal_div = $('.minha-modal');

botao_abrir_modal.on('click', function (event) {
    event.preventDefault();
    console.log('botao_abrir_modal click event');
    var modal = $(modal_template);
    modal.attr('id', 'minhamodal2');
    modal.on('hidden', function (e) {
        $('[data-scriptautoadded]').off().remove();
        $('#minhamodal2').remove();
    });

    var do_ajax = function (botao_el) {
        console.log('do_ajax');

        var botao = $(botao_el);
        var url = botao.attr('href');
        var modal_body = $(".modal-body", modal);
        // // console.log(modal);
        // // modal.startLoading();
        var ajax_request_cfg = {
            url: url,
            cache: false,
            method: "GET"
        };
        var request = $.ajax(ajax_request_cfg);

        request.done(function (data) {
            var response_data = $(data);
            var scripts = response_data.find('script');
            var css = response_data.find('link');
            $('script', response_data).remove();
            $('link', response_data).remove();
            console.log('tamanho css: ' + css.length);
            console.log('tamanho scripts: ' + scripts.length);

            // executar_apos_carregar([scripts], modal);
            // response_data = response_data.html();
            console.log(response_data);
            scripts.attr('data-scriptautoadded', 'true');
            css.attr('data-scriptautoadded', 'true');
            console.log(scripts);
            $('head').append(css);
            $('body').append(scripts);
            // modal_div.removeClass('bah');
            modal_body.html(response_data);
            // modal


            // $(window).ready(function () {
            //     // modal.iziModal('stopLoading');
            //     modal_body.fadeIn();
            //     console.log("hahah");
            // });
            //
        });
        // request.fail(function (jqXHR, textStatus) {
        //     console.log('ajax get fail');
        //     alert("Request failed: " + textStatus);
        // });
        request.always(function (jqXHR, textStatus, errorThrown) {
            // 1.4.2 the method name is recalculateLayout
            // but on 1.5.0 beta, the method was renamed to recalcLayout
            // modal.iziModal('stopLoading');
            // modal.iziModal('recalcLayout');
            // that.attr('disabled', false);
            //
            $('body').append(modal);
            modal.modal('show');
            setTimeout(function () {
                console.log("focou");
                $(".iziModal-content", modal).find(':input:not(button):enabled:visible:first').focus();
            }, 500);
        });
        //
    };


    do_ajax(botao_abrir_modal);


});


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



/**
 * Created by luzfcb on 31/03/17.
 */
'use strict';
(function (window, $) {
    window.luzfcb_modal = window.luzfcb_modal || {};
    $(document).bind('destroymodal', function (e) {
        // deleta tudo.
        console.log('passou no destroymodal');
        $('[data-scriptautoadded]').off().remove();
        var minha_m = $('#minhamodalfoda');
        $('[data-autocomplete-light-function=select2]', minha_m).select2("destroy");
        minha_m.remove();
        window.luzfcb_modal.modal_ized = undefined;
        window.luzfcb_modal.modal_div = undefined;
        $.fn.getFormPrefix = undefined;

        yl = undefined;
    });
    function iniciar(botao_abrir_modal, url) {


        var modal_template="";
        modal_template += "    <div class=\"minha-modal bah\" id=\"minhamodalfoda\">";
        modal_template += "        <div style=\"width: 15%; height: 15%\"><\/div>";
        modal_template += "    <\/div>";

        var luzfcb_modal = window.luzfcb_modal;


        botao_abrir_modal.off('click.openmodal').on('click.openmodal', function (event) {
            event.preventDefault();
            luzfcb_modal.botao_abrir_modal = $(this);
            luzfcb_modal.botao_abrir_modal.attr('luzfcbmodal-enabled', true);
            var esta_desabilitado = luzfcb_modal.botao_abrir_modal.attr('disabled');
            if (!esta_desabilitado) {
                luzfcb_modal.botao_abrir_modal.attr('disabled', true);
                // cria elemento virtual apartir do template
                var modal_div = $(modal_template);
                console.log('botao_abrir_modal click event');
                // adiciona o elemento no body

                $('body').append(modal_div);

                luzfcb_modal.modal_div = modal_div;

                // ########################################################################
                // ativa a modal no elemento modal_div
                var modal_ized = modal_div.iziModal({
                    autoOpen: false,
                    top: '10%',
                    // width: '50px',
                    // height: '50px',
                    restoreDefaultContent: false,
                    onOpening: function (modal) {
                        modal.startLoading();

                    },
                    onOpened: function (modal) {
                        // $(modal).iziModal('recalculateLayout');
                    },
                    onClosed: function (modal) {
                        // clean the content of modal
                        // $(".iziModal-content").html('');
                        console.log('fechou modal');
                        $(document).trigger('destroymodal');
                        if (luzfcb_modal.botao_abrir_modal.attr('luzfcbmodal-enabled')) {
                            luzfcb_modal.botao_abrir_modal.attr('disabled', false);
                        }
                        // luzfcb_modal.botao_abrir_modal.off('click.openmodal');
                        // modal_div.removeClass('bah').addClass('bah');

                    }
                });
                luzfcb_modal.modal_ized = modal_ized;
                modal_ized.on('opened', function (e) {
                    do_ajax(botao_abrir_modal, $(this), url);
                    $(this).iziModal('stopLoading');
                });
                modal_ized.on('onClosed', function (e) {
                    // modal_div.iziModal('destroy');

                });

                //#########################################
                var do_ajax = function (botao_el, modal, url) {
                    console.log('do_ajax');

                    var botao = $(botao_el);


                    // var izi_content = $(".iziModal-content", modal);
                    var izi_content = $(".iziModal-content", modal);
                    var ajax_request_cfg = {
                        url: url,
                        cache: false,
                        method: "GET"
                    };
                    var request = $.ajax(ajax_request_cfg);

                    request.done(function (data) {
                        var response_data = $('<div>' + data + '</div>');
                        var scripts = response_data.find('script');
                        var css = response_data.find('link');
                        $('script', response_data).remove();
                        $('link', response_data).remove();
                        scripts.attr('data-scriptautoadded', 'true');
                        css.attr('data-scriptautoadded', 'true');
                        $('head').append(css);
                        $('body').append(scripts);
                        modal_div.removeClass('bah');
                        izi_content.html(response_data);
                        response_data = undefined;
                        scripts = undefined;
                        css = undefined;

                    });
                    request.fail(function (jqXHR, textStatus) {
                        console.log('ajax get fail');
                        alert("Request failed: " + textStatus);
                    });
                    request.always(function (jqXHR, textStatus, errorThrown) {
                        setTimeout(function () {
                            console.log("focou");
                            var first_el = $(".iziModal-content", modal).find(':input:not(button):enabled:visible:first');
                            if (first_el.has('select2-hidden-accessible')) {
                                first_el.select2('focus');
                            } else {
                                first_el.focus();
                            }
                        }, 500);
                    });
                };
                // abre a modal
                modal_ized.iziModal('open');
            }

        });

    }

    $('a[luzfcbmodal]').each(function (key, item) {
        var el = $(item);
        var url = el.attr('href') || el.data('luzfcbmodal-url');
        iniciar(el, url);
    });
    $('button[luzfcbmodal]').each(function (key, item) {
        var el = $(item);
        var url = el.data('luzfcbmodal-url');
        iniciar(el, url);
    });


})(window, jQuery);



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
        window.luzfcb_modal.modal_ized.destroy();
        window.luzfcb_modal.modal_ized = null;
        window.luzfcb_modal.modal_div = null;
        $.fn.getFormPrefix = null;

        yl = null;
    });
    $(document).bind('luzfcbmodal:ajaxdone', function (e) {
        console.log(e);
        console.log(e.returned_data);
        console.log(e.form);
        console.log(e.modal);
        window.location.reload(true);
        e.modal.close();


    });
    function get_save_button(the_form, modal) {
        var submit_buttons = $('button[type=submit],input[type=submit]', the_form);
        var label = submit_buttons.text() || submit_buttons.attr('value') || 'Salvar';
        submit_buttons.remove();
        modal.addFooterBtn(label, 'btn btn-success form-btn-salvar-modal', function () {
            the_form.submit();
        });
        return $('.tingle-modal > .form-btn-salvar-modal');
    }

    function process_form_if_exists(modal) {
        var the_forms = $(".tingle-modal-box__content").find('form');
        $(the_forms).each(function () {
            var $formulario = $(this);
            var excluir_modal_agora = false;
            var $botao_salvar = get_save_button($formulario, modal);
            // var modal = $formulario.parents('.modal');
            var div_modal = $formulario.parents('.div-modal');
            // $botao_salvar.click(function (event) {
            //     event.preventDefault();
            //     $formulario.submit();
            //
            // });

            // $(modal).on('hidden.bs.modal', function () {
            //     var inputs = $(':input:enabled:not([readonly]):not([disabled])', $formulario);
            //     clean_form_errors(inputs, $formulario);
            //     if (excluir_modal_agora === true) {
            //         //$(this).exclude();
            //         div_modal.remove();
            //         window.location.reload(true);
            //     }
            // });

            $formulario.submit(function (event) {
                // Stop form from submitting normally
                event.preventDefault();
                $botao_salvar.prop('disabled', true);
                var $form = jQuery(this);
                var conteudo = $form.serializeArray();
                clean_form_errors(conteudo, $form);
                var url = $form.attr("action").replace(/\s/g, "");
                console.log('url: ' + url);
                var posting = $.post(url, conteudo, 'JSON');

                // process fail logic
                posting.fail(function (jqXHR, textStatus, errorThrown) {

                    console.log('textStatus: ' + textStatus);
                    console.log('errorThrown:' + errorThrown);
                    var response = jqXHR.responseJSON;

                    mark_fields_with_errors(response.errors, $form);

                });
                // Put the results in a div
                posting.done(function (data, textStatus, jqXHR) {

                    var returned_data = jQuery(data);
                    console.log("done");
                    // modal.close();
                    var event = jQuery.Event( "luzfcbmodal:ajaxdone" );
                    event.returned_data = returned_data;
                    event.form = $form;
                    event.modal = modal;
                    $(document).trigger(event);

                });
                posting.always(function (data, textStatus, errorThrown) {


                    $botao_salvar.prop('disabled', false);
                });
            }).bind('ajax:complete', function () {

                // tasks to do
                console.log("ajax completo");


            });
        });

    }

    var clean_form_errors = function (serialized_array, form) {

        for (var item in serialized_array) {
            if (serialized_array.hasOwnProperty(item)) {
                var input_id = 'id_' + serialized_array[item].name;
                var label_search = "label[for='" + input_id + "']";
                $(label_search).parents('div:first').removeClass('has-error');
                $('.autoadded', form).remove();
            }
        }
    };

    var mark_fields_with_errors = function (errors, form) {
        for (var key in errors) {
            if (errors.hasOwnProperty(key)) {
                var el_text = '<p id="error_1_id_' + key + '" class="help-block autoadded"> <strong>' + errors[key] + '</strong></p>';
                var p_element = $(el_text);
                var input_id = 'id_' + key;
                var label_search = "label[for='" + input_id + "']";
                $('#hint_id_' + key, form).before(p_element);

                $(label_search).parents('div:first').removeClass('has-error').addClass('has-error');
            }
        }
    };


    function iniciar_modal(botao_abrir_modal, url) {


        var modal_template = "";
        modal_template += "    <div class=\"minha-modal bah\" id=\"minhamodalfoda\">";
        modal_template += "        <div style=\"width: 15%; height: 15%\"><\/div>";
        modal_template += "    <\/div>";

        var luzfcb_modal = window.luzfcb_modal;


        botao_abrir_modal.off('click.openmodal').on('click.openmodal', function (event) {
            event.preventDefault();
            luzfcb_modal.botao_abrir_modal = $(this);
            luzfcb_modal.botao_abrir_modal.attr('luzfcbmodal-enabled', true);
            var esta_desabilitado = luzfcb_modal.botao_abrir_modal.attr('disabled');
            $('body > div,nav,section,header,footer').not('.tingle-modal').removeClass('tingle-content-wrapper2').addClass('tingle-content-wrapper2');
            //$('body').removeClass('tingle-content-wrapper').addClass('tingle-content-wrapper');
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

                var modal_ized = new tingle.modal({
                    footer: true,
                    stickyFooter: true,
                    // closeLabel: "Close",
                    // cssClass: ['custom-class-1', 'custom-class-2'],
                    onOpen: function (m) {
                        console.log('modal open');
                        do_ajax(botao_abrir_modal, luzfcb_modal.modal_ized, url);
                    },
                    onClose: function () {
                        console.log('fechou modal');
                        $(document).trigger('destroymodal');
                        if (luzfcb_modal.botao_abrir_modal.attr('luzfcbmodal-enabled')) {
                            luzfcb_modal.botao_abrir_modal.attr('disabled', false);
                        }
                    },
                    beforeClose: function () {
                        // here's goes some logic
                        // e.g. save content before closing the modal
                        return true; // close the modal
                        //return false; // nothing happens
                    }
                });

                luzfcb_modal.modal_ized = modal_ized;


                //#########################################
                var do_ajax = function (botao_el, modal, url) {
                    console.log('do_ajax');

                    var botao = $(botao_el);


                    var ajax_request_cfg = {
                        url: url,
                        cache: true,
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
                        var div = document.createElement('div');
                        div.innerHTML = response_data.html();
                        modal.setContent(div);
                        process_form_if_exists(modal);
                        response_data = null;
                        scripts = null;
                        css = null;

                    });
                    request.fail(function (jqXHR, textStatus) {
                        console.log('ajax get fail');
                        alert("Request failed: " + textStatus);
                    });
                    request.always(function (jqXHR, textStatus, errorThrown) {
                        setTimeout(function () {
                            console.log("focou");
                            var first_el = $(".tingle-modal-box__content").find(':input:not(button):not([disabled]):enabled:visible:first');
                            if (first_el.has('select2-hidden-accessible')) {
                                first_el.select2('focus');
                                console.log(first_el.attr('id') + 'select2');
                            } else {
                                first_el.focus();
                                console.log(first_el.attr('id') + 'normal');
                            }

                        }, 300);
                    });
                };
                // abre a modal
                modal_ized.open();
            }

        });

    }

    $('a[luzfcbmodal]').each(function (key, item) {
        var el = $(item);
        var url = el.attr('href') || el.data('luzfcbmodal-url');
        iniciar_modal(el, url);
    });
    $('button[luzfcbmodal]').each(function (key, item) {
        var el = $(item);
        var url = el.data('luzfcbmodal-url');
        iniciar_modal(el, url);
    });


})(window, jQuery);



/**
 * Created by luzfcb on 11/04/17.
 * based on: https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */

// onde será colocado o contedo buscado por AJAX
(function (window, document, jQuery) {
    'use strict';
    var body_el = $("body");
    var id_modal = 'autocreatedmodal';
    var m_template = "<div id=\"" + id_modal + "\"></div>";
    var $the_modal = $(m_template);
    var $temporary_background_image = $("<img  width=\"200px\" height=\"200px\"  src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJAQMAAADaX5RTAAAAA1BMVEVMaXFNx9g6AAAAAXRSTlMAQObYZgAAAAtJREFUeNpjYMAJAAAbAAFZmD3qAAAAAElFTkSuQmCC\">");
    // inicializa a modal
    $the_modal.iziModal({
        zindex: 1050,
        bodyOverflow: false,
        autoOpen: false,
        top: '40px',
        history: false

    });

    body_el.append($the_modal);
    var $the_modal_body = $('.iziModal-content', $the_modal);

    window.getSucessUrl = function (el) {
        var self = $(el);
        var value_to_return = false;
        var sucess_url_data = self.data('sucess-url');

        if (!(typeof sucess_url_data === "undefined")) {
            var current_location = new URL(location);
            var sucess_url = new URL(sucess_url_data, current_location);
            if (sucess_url.host === current_location.host) {
                value_to_return = sucess_url;
            }
        }
        return value_to_return;
    };

    function dealWithIt(event) {
        // lê o cache
        $the_modal_body.html($temporary_background_image);
        $the_modal.iziModal('startLoading');
        $the_modal.iziModal('open');
        var id_ = getOrAndApplyId(this);
        var cache = getCache(id_);
        event.preventDefault();


        if (typeof cache === 'undefined') {
            // se quando o usuario clicar no link ainda não tiver sido feito o prefetch do conteúdo,
            // executar o fetch no ato.
            var self = $(this);
            ////console.log('cache nao existe, criando novo cache');
            fetchContent({url: self.attr('href'), linkId: self.data('id')})
                .then(function (fragment) {
                    ////console.log('executou fetchContent');
                    ////console.log('fragment: ' + fragment);
                    // $whereToPutIt.append($(fragment));
                    var documentFragment = document.createElement('div');
                    var ca = getCache(id_);
                    documentFragment.innerHTML = ca.fragment;
                    var d_to_insert = $(documentFragment);
                    process_form_if_exists(this, $the_modal, d_to_insert);
                    // $(documentFragment).hide();
                    $the_modal_body.html(documentFragment);
                    //console.log('parando loading');
                    $the_modal.iziModal('stopLoading');
                });
        } else {
            // se tivermos feito o prefetch quando o usuário clicar no link, buscar do cache
            var documentFragment = document.createElement('div');
            documentFragment.innerHTML = cache.fragment;
            var d_to_insert = $(documentFragment);
            process_form_if_exists(this, $the_modal, d_to_insert);
            $the_modal_body.html(documentFragment);
            //console.log('parando loading');
            $the_modal.iziModal('stopLoading');
        }


    }

    function focus_on_first_enabled_input(modal_body) {
        //console.log('focus_on_first_enabled_input modal_body');
        //console.log(modal_body);
        var first_el = modal_body.find(':input:not(button):enabled:visible:first');
        if (first_el.has('select2-hidden-accessible')) {
            try {
                first_el.select2('focus');
            } catch (err) {

            }
        } else {
            first_el.focus();
        }
    }

    body_el.on('opening', '#' + id_modal, function (e) {
        //console.log('Modal is opening');
    });
    body_el.on('opened', '#' + id_modal, function (e) {
        //console.log('Modal is opened');
        focus_on_first_enabled_input($the_modal_body);
        var event = jQuery.Event("ajaxmodal:opened");
        body_el.trigger(event, {
                modal: $the_modal,
                modal_body: $the_modal_body
            }
        );

    });

    body_el.on('closing', '#' + id_modal, function (e) {
        //console.log('Modal is closing');
    });
    body_el.on('closed', '#' + id_modal, function (e) {
        //console.log('Modal is closed');
    });

    // seleciona os links que queremos rodar o AJAX no onclick
    $('a[data-ajaxmodal]').each(function (index, el) {
        //console.log('iniciou modal');
        $(el).on('click', dealWithIt);
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

    function process_form_if_exists(original_element, the_modal, modal_body) {
        var sucess_url = getSucessUrl(original_element);
        var the_forms = $(modal_body).find('form');
        //console.log('the_modal');
        //console.log(the_modal);
        //console.log('modal_body');
        //console.log(modal_body);
        $(the_forms).each(function () {
            //console.log('achou formulario');
            var $formulario = $(this);
            var excluir_modal_agora = false;
            // var $botao_salvar = get_save_button($formulario, modal_body);
            var $botao_salvar = $('button[type=submit],input[type=submit]', modal_body);
            var $botao_cancelar = $('button.cancelar', modal_body);
            //console.log('$botao_salvar');
            //console.log($botao_salvar);
            // var modal = $formulario.parents('.modal');
            var div_modal = $formulario.parents('.div-modal');
            $botao_salvar.on('click', function (event) {
                event.preventDefault();
                //console.log('clicou');
                $formulario.submit();

            });
            $botao_cancelar.on('click', function (event) {
                event.preventDefault();
                //console.log('clicou');
                the_modal.iziModal('close');

            });
            $formulario.submit(function (event) {
                // Stop form from submitting normally
                event.preventDefault();
                $botao_salvar.prop('disabled', true);
                var $form = jQuery(this);
                var conteudo = $form.serializeArray();
                clean_form_errors(conteudo, $form);
                var url = $form.attr("action").replace(/\s/g, "");
                //console.log('url: ' + url);
                var posting = $.post(url, conteudo, 'JSON');

                // process fail logic
                posting.fail(function (jqXHR, textStatus, errorThrown) {

                    //console.log('textStatus: ' + textStatus);
                    //console.log('errorThrown:' + errorThrown);
                    if (errorThrown === "NOT FOUND" || errorThrown === "FORBIDDEN") {
                        var event = jQuery.Event("ajaxmodal:ajax-form-post-error-notfound");
                        body_el.trigger(event, {
                            post_url: url,
                            post_data: conteudo,
                            modal: the_modal,
                            sucess_url: sucess_url
                        });
                    } else {
                        var response = jqXHR.responseJSON;

                        mark_fields_with_errors(response.errors, $form);
                    }
                });
                // Put the results in a div
                posting.done(function (data, textStatus, jqXHR) {

                    var returned_data = jQuery(data);
                    //console.log("done");
                    // modal.close();
                    var event = jQuery.Event("ajaxmodal:ajax-form-post-done");

                    var parans = {
                        returned_data: returned_data,
                        modal: the_modal,
                        sucess_url: sucess_url
                    };
                    //console.log("deveria redirecionar para: " + parans.sucess_url);
                    body_el.trigger(event, parans);

                });
                posting.always(function (data, textStatus, errorThrown) {


                    $botao_salvar.prop('disabled', false);
                });
            }).on('ajax:complete', function () {

                // tasks to do
                //console.log("ajax completo");


            });
        });

    }

    var clean_form_errors = function (serialized_array, form) {

        for (var item in serialized_array) {
            if (serialized_array.hasOwnProperty(item)) {
                var input_id = 'id_' + serialized_array[item].name;
                var label_search = "label[for='" + input_id + "']";
                $(label_search).parents('div:first').removeClass('has-error').removeClass('error');
                $('.autoadded', form).remove();
            }
        }
    };

    var mark_fields_with_errors = function (errors, form) {
        for (var key in errors) {
            if (errors.hasOwnProperty(key)) {
                var el_text = '<p id="error_1_id_' + key + '" class="help-block alert alert-danger autoadded"> <strong>' + errors[key] + '</strong></p>';

                var p_element = $(el_text);
                var label_search = '';

                var input_id = 'id_' + key;
                var hint_id = '#hint_id_' + key;

                if (form.context.action.includes('assinarfinalizar')){
                    input_id = 'id_assinarfinalizar-' + key;
                    hint_id = '#hint_id_assinarfinalizar-' + key
                }

                label_search = "label[for='" + input_id + "']";
                $(hint_id, form).before(p_element);


                $(label_search).parents('div:first').removeClass('has-error').removeClass('error').addClass('has-error').addClass('error');
            }
        }
    };


    body_el.on('ajaxmodal:opened', function (e, parans) {
        //console.log(e);
        //console.log('ajaxmodal:opened');
        //console.log(parans);
        //process_form_if_exists(parans.modal, parans.modal_body);
    });

    body_el.on("ajaxmodal:ajax-form-post-done", function (e, parans) {
        parans.modal.iziModal('close');
        //console.log("antes deveria redirecionar para: " + parans.sucess_url);
        if (!parans.sucess_url === false) {
            //console.log("deveria redirecionar para: " + parans.sucess_url);
            window.location.replace(parans.sucess_url);
        } else {
            //console.log("reload (ou deveria)");
            window.location.reload(true);
        }
        //console.log("depois deveria redirecionar para: " + parans.sucess_url);

        //process_form_if_exists(parans.modal, parans.modal_body);
    });
    body_el.on("ajaxmodal:ajax-form-post-error-notfound", function (e, parans) {
        parans.modal.iziModal('close');
        //console.log('nao existente');
        window.location.reload(true);
        //process_form_if_exists(parans.modal, parans.modal_body);
    });


})(window, document, jQuery);



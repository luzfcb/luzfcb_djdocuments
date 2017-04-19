/**
 * Created by luzfcb on 11/04/17.
 * based on: https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */

// onde será colocado o contedo buscado por AJAX
(function () {


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

    $("body").append($the_modal);
    var $the_modal_body = $('.iziModal-content', $the_modal);

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
            //console.log('cache nao existe, criando novo cache');
            fetchContent({url: self.attr('href'), linkId: self.data('id')})
                .then(function (fragment) {
                    //console.log('executou fetchContent');
                    //console.log('fragment: ' + fragment);
                    // $whereToPutIt.append($(fragment));
                    var documentFragment = document.createElement('div');
                    documentFragment.innerHTML = fragment;
                    // $(documentFragment).hide();
                    $the_modal_body.html($(documentFragment));
                    console.log('parando loading');
                    $the_modal.iziModal('stopLoading');
                });
        } else {
            // se tivermos feito o prefetch quando o usuário clicar no link, buscar do cache
            $the_modal_body.html($(cache.fragment));
            console.log('parando loading');
            $the_modal.iziModal('stopLoading');
        }


    }

    function focus_on_first_enabled_input(modal_body) {
        console.log('focus_on_first_enabled_input modal_body');
        console.log(modal_body);
        var first_el = modal_body.find(':input:not(button):enabled:visible:first');
        if (first_el.has('select2-hidden-accessible')) {
            first_el.select2('focus');
        } else {
            first_el.focus();
        }
    }

    $(document).on('opening', '#' + id_modal, function (e) {
        console.log('Modal is opening');
    });
    $(document).on('opened', '#' + id_modal, function (e) {
        console.log('Modal is opened');
        focus_on_first_enabled_input($the_modal_body);
        var event = jQuery.Event("ajaxmodal:opened");
        $(document).trigger(event, {
                modal: $the_modal,
                modal_body: $the_modal_body
            }
        );

    });

    $(document).on('closing', '#' + id_modal, function (e) {
        console.log('Modal is closing');
    });
    $(document).on('closed', '#' + id_modal, function (e) {
        console.log('Modal is closed');
    });

    // seleciona os links que queremos rodar o AJAX no onclick
    $('a[data-ajaxmodal]').each(function (index, el) {
        console.log('iniciou modal');
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

    function process_form_if_exists(the_modal, modal_body) {
        var the_forms = $(modal_body).find('form');
        console.log('the_modal');
        console.log(the_modal);
        console.log('modal_body');
        console.log(modal_body);
        $(the_forms).each(function () {
            console.log('achou formulario');
            var $formulario = $(this);
            var excluir_modal_agora = false;
            // var $botao_salvar = get_save_button($formulario, modal_body);
            var $botao_salvar = $('button[type=submit],input[type=submit]', modal_body);
            console.log('$botao_salvar');
            console.log($botao_salvar);
            // var modal = $formulario.parents('.modal');
            var div_modal = $formulario.parents('.div-modal');
            $botao_salvar.click(function (event) {
                event.preventDefault();
                console.log('clicou');
                $formulario.submit();

            });

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
                    var event = jQuery.Event("luzfcbmodal:ajaxdone");
                    event.returned_data = returned_data;
                    event.form = $form;
                    event.modal = modal;
                    $(document).trigger(event, 'alo to aqui');

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


    $(document).bind('ajaxmodal:opened', function (e, parans) {
        console.log(e);
        console.log('ajaxmodal:opened');
        console.log(parans);
        process_form_if_exists(parans.modal, parans.modal_body);
    });

})();



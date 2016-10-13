/**
 * Created by luzfcb on 01/03/16.
 */


(function (window, jQuery, Pace, humane, luzfcb) {
    "use strict";

    var conteudo_modificado = {};

    luzfcb.editor.debug = luzfcb.editor.debug || false;
    var selected_style_name = luzfcb.editor.ckeditor_style_name;
    var selected_style_full_url = luzfcb.editor.ckeditor_style_full_url;
    var selected_style = '' + selected_style_name + ':' + selected_style_full_url;
    var ckeditor_contentsCss = luzfcb.editor.ckeditor_contentsCss;
    var msg_nao_salvo = luzfcb.editor.msg_nao_salvo;

    var $botao_salvar = luzfcb.editor.$botao_salvar;
    var $formulario = luzfcb.editor.$formulario;

    var $status_bar = jQuery("#status-bar");
    var $ckeditor_enable_form_fields = jQuery("[data-djckeditor]");
    var $main_div = jQuery(".maindiv");
    var $menu_superior = jQuery("#menu-superior");
    var $conteudo = jQuery('#conteudo');

    function log_to_console(msg) {
        if (luzfcb.editor.debug) {
            console.log(msg);
        }
    }

    function get_ckenabledElementIds() {
        return $ckeditor_enable_form_fields.map(function () {
            return this.id;
        }).get();
    }

    var ckenabledElementIds = get_ckenabledElementIds();


    function ativarDesativarSalvar() {
        for (var instance in CKEDITOR.instances) {
            var id_elemento = "" + instance;
            conteudo_modificado[id_elemento] = false;
            //verifica se ha modificacoes no conteudo desde o carregamento do editor
            // ou desde a execucao do metodo resetDirty
            //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-checkDirty
            conteudo_modificado[id_elemento] = !!CKEDITOR.instances[id_elemento].checkDirty();
        }
        var ativar = false;
        for (var key in conteudo_modificado) {
            if (conteudo_modificado.hasOwnProperty(key)) {
                ativar = conteudo_modificado[key];
            }
            if (ativar) {
                break;
            }
        }
        if (ativar) {
            $botao_salvar.prop('disabled', false);
        }
        else {
            $botao_salvar.prop('disabled', true);
        }
        return ativar;

    }

    function antes_de_sair_da_pagina(evt) {
        //executado antes do mudar/sair/fecha a pagina
        var item_nao_salvo = false;
        for (var instance in CKEDITOR.instances) {
            if (CKEDITOR.instances.hasOwnProperty(instance)) {
                //verifica se ha modificacoes no conteudo desde o carregamento do editor
                // ou desde a execucao do metodo resetDirty
                //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-checkDirty
                if (CKEDITOR.instances[instance].checkDirty()) {
                    item_nao_salvo = true;
                }
            }
        }
        log_to_console('Antes de sair');
        if (item_nao_salvo) {
            return evt.returnValue = msg_nao_salvo;
        }
    }

    function corrigir_padding_conteudo() {

        var altura_menu_superior = parseInt($menu_superior.css('height').replace(/[^-\d\.]/g, ''));
        var adicional_altura = 130;

        var valor = "".concat(String(altura_menu_superior + adicional_altura)).concat("px");
        $conteudo.css('padding-top', valor);
        log_to_console('corrigir_padding_conteudo');
    }

    // jQuery(window).resize(function () {
    //     corrigir_padding_conteudo();
    // });

    function register_windows_page_events() {
        //executado antes do mudar/sair/fecha a pagina

        if (window.addEventListener) {
            //evento executado ao redimencionar a janela
            window.addEventListener('resize.corrigir_padding_conteudo', corrigir_padding_conteudo, false);
            //evento executado ao sair da pagina/fechar a pagina ou janela
            window.addEventListener('beforeunload', antes_de_sair_da_pagina, false);
        }
        else {
            window.attachEvent('onbeforeunload', antes_de_sair_da_pagina);
            window.attachEvent('resize.corrigir_padding_conteudo', corrigir_padding_conteudo);
        }

    }

    function startCkEditor(ckeditor_config) {
        ckenabledElementIds.map(function (id_elemento) {
            var current_config = ckeditor_config;
            var el = document.getElementById(id_elemento);
            if (el.hasAttribute('autofocus')){
                var new_config = create_ckeditor_config();
                new_config.startupFocus = true;
                log_to_console('autofocus em elemento id=' + id_elemento);
                current_config = new_config;
            }
            if (luzfcb.editor.debug) {
                current_config.toolbar_Basic[4]['items'] =  ['Source', 'Zoom'];
            }

            CKEDITOR.replace(id_elemento, current_config);
            // vicula a funcao para controlar a ativacao/desativacao do botao salvar, no evento de quando ha mudancas no editor
            CKEDITOR.instances[id_elemento].on('change', function () {
                ativarDesativarSalvar();
            });
        });
        ativarDesativarSalvar();
    }

    function create_ckeditor_config() {
        var new_config = {
            extraPlugins: [
                'sharedspace',

                'autolink',
                'autogrow',
                "base64image",
                "dialog", // required by base64image
                "dialogui", // required by base64image
                "maiuscula",
                "extenso",
                // "zoom"
                // habilita o plugin stylesheetparser: http://ckeditor.com/addon/stylesheetparser
                // requer desabilitar o suporte a Advanced Content Filter
                //'stylesheetparser'
                // end habilita o plugin stylesheetparser

            ].join(),
            removePlugins: 'resize,maximize,magicline',
            removeButtons: 'resize,Maximize',
            sharedSpaces: {
                'top': 'top',
                'bottom': 'bottom'
            },
            stylesSet: selected_style,
            contentsCss: ckeditor_contentsCss,
            // format_p: { element: 'p', attributes: { class: 'Texto_Justificado_Recuo_Primeira_Linha' }},
            startupShowBorders: false,
            autoGrow_onStartup: true,
            autoGrow_minHeight: 0,
            autoGrow_bottomSpace: 0,
            toolbar: 'Basic',
            toolbar_Basic: [
                {
                    name: 'basicstyles',
                    items: ['Find', 'Replace', '-', 'RemoveFormat', 'Bold', 'Italic', 'Underline', 'Strike', 'Maiuscula', 'Minuscula', 'TextColor', 'BGColor']
                },
                {
                    name: 'clipboard',
                    items: ['Cut', 'Copy', 'PasteFromWord', 'PasteText', '-', 'Undo', 'Redo', 'ShowBlocks']
                },
                {
                    name: 'paragraph',
                    items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'base64image', '-', 'Blockquote']
                },
                {name: 'insert', items: ['Table', 'SpecialChar', 'HorizontalRule', 'Extenso']},
                {name: 'document', items: ['Zoom']},
                {name: 'styles', items: ['Styles']}

            ],
            // desativa o Advanced Content Filter
            // http://docs.ckeditor.com/#!/guide/dev_advanced_content_filter
            // para poder utilizar o plugin stylesheetparser http://ckeditor.com/addon/stylesheetparser
            //allowedContent: true,
            // end desativa o Advanced Content Filter
            base64image_disableUrlImages: true,
            justifyClasses: ['AlignLeft', 'AlignCenter', 'AlignRight', 'AlignJustify']


        };
        return new_config;
    }

    // configuracao das intancias do ckeditor
    luzfcb.editor.ckeditor_config = create_ckeditor_config();


    function init_page_scripts() {
        register_windows_page_events();
        startCkEditor(luzfcb.editor.ckeditor_config);

    }


    //http://brack3t.com/ajax-and-django-views.html
    //https://github.com/wavded/humane-js
    //https://github.com/alertifyjs/alertify.js
    //versao 2
    jQuery(document).ready(function () {


        var requestRunning = false;


        function clear_form_field_errors(form) {
            jQuery(".ajax-error", jQuery(form)).remove();
            jQuery(".error", jQuery(form)).removeClass("error");
        }


        $formulario.submit(function (event) {
            // Stop form from submitting normally
            event.preventDefault();


            if (requestRunning) { // don't do anything if an AJAX request is pending
                return;
            }

            for (var instance in CKEDITOR.instances) {
                if (CKEDITOR.instances.hasOwnProperty(instance)) {
                    //atualiza o textarea vinculado ao editor, porque ao editar, voce nao esta editando o textarea
                    // e sim o conteudo de um iframe criado pelo ckeditor.
                    //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-updateElement
                    CKEDITOR.instances[instance].updateElement();
                }
            }

            var $form = jQuery(this);
            var conteudo = $form.serializeArray();
            var url = $form.attr("action").replace(/\s/g, "");

            clear_form_field_errors($form);
            requestRunning = true;
            // Send the data using post
            // parametros url, data, callback, type
            // sendo que callback é sucess
            var posting = $.post(url, conteudo, 'JSON');

            // Put the results in a div
            posting.fail(function (jqXHR, textStatus, errorThrown) {


                var errors = jqXHR.responseJSON;

                log_to_console(errors);
                var msg = "Erro ao salvar documento" + errors.document_number + "\n";
                humane.log(msg, {
                    timeout: 2500,
                    clickToClose: true,
                    addnCls: 'humane-error'
                });


            });
            // Put the results in a div
            posting.done(function (data, textStatus, jqXHR) {
                log_to_console("done data:", data);
                log_to_console("done textStatus:", textStatus);
                log_to_console("done jqXHR:", jqXHR);
                // var content = jQuery(data);
                log_to_console(jQuery(data));
                for (var editor_instance in CKEDITOR.instances) {
                    if (CKEDITOR.instances.hasOwnProperty(editor_instance)) {
                        // http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-resetDirty
                        CKEDITOR.instances[editor_instance].resetDirty();
                        //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-resetUndo
                        CKEDITOR.instances[editor_instance].resetUndo();

                        conteudo_modificado[editor_instance] = false;
                    }
                }
                ativarDesativarSalvar();
                var mensagem = "Documento N° " + data.document_number + " salvo com sucesso!";
                humane.log(mensagem, {
                    timeout: 2500,
                    clickToClose: true,
                    addnCls: 'humane-sucess'
                });
                $status_bar.empty().append('Documento: ' + data.identificador_versao);
            });
            posting.always(function (data, textStatus, errorThrown) {
                log_to_console("always");
                requestRunning = false;
            });
        }).bind('ajax:complete', function () {

            // tasks to do
            log_to_console("ajax completo");


        });
        $botao_salvar.click(function () {

            $formulario.submit();

        });


    });


    init_page_scripts();
    // Pace.on('hide', function () {
    //     //inicia os scripts basicos da pagina
    //
    //     $main_div.fadeIn("fast");
    //     corrigir_padding_conteudo();
    //     for (var instance in CKEDITOR.instances) {
    //         if (CKEDITOR.instances.hasOwnProperty(instance)) {
    //             //instance.editor.fire( 'click' );
    //             CKEDITOR.instances[instance].execCommand('autogrow');
    //         }
    //
    //     }
    // });
    function startall() {
        $main_div.fadeIn("fast");
        corrigir_padding_conteudo();
        for (var instance in CKEDITOR.instances) {
            if (CKEDITOR.instances.hasOwnProperty(instance)) {
                //instance.editor.fire( 'click' );
                CKEDITOR.instances[instance].execCommand('autogrow');
            }

        }
    }

    luzfcb.editor.startall = startall;

})(window, jQuery, Pace, humane, window.luzfcb || (window.luzfcb = {}));


jQuery(document).on('click', '.djpopup2', function () {
    "use strict";
    var popUpObj;
    //var id = $(this).attr('id');
    // var id = uuid.v4();
    var url_to_open = $(this).prop("href");
    var desabilitado = $(this).attr("disabled");

    if (!desabilitado) {
        var popup_windows_options = "toolbar=no," +
            "scrollbars=yes," +
            "location=no," +
            "statusbar=no," +
            "menubar=no," +
            "resizable=0," +
            "width=980," +
            "height=980," +
            //"left = 490," +
            //"top=300"
            "";

        popUpObj = window.open(url_to_open, 'print_diag', popup_windows_options);
        if (window.focus) {
            popUpObj.focus();
        }
    }
    return false;
});

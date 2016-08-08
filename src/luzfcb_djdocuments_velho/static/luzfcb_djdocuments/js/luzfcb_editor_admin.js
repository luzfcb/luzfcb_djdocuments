/**
 * Created by luzfcb on 11/03/16.
 */
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

    var $ckeditor_enable_form_fields = jQuery("[data-djckeditor]");
    var $main_div = jQuery(".maindiv");

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




    function antes_de_sair_da_pagina(evt) {
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

        // var altura_menu_superior = parseInt($menu_superior.css('height').replace(/[^-\d\.]/g, ''));
        // var adicional_altura = 130;
        //
        // var valor = "".concat(String(altura_menu_superior + adicional_altura)).concat("px");
        // $conteudo.css('padding-top', valor);
        // log_to_console('corrigir_padding_conteudo');
    }

    // jQuery(window).resize(function () {
    //     corrigir_padding_conteudo();
    // });

    function register_windows_page_events() {

        if (window.addEventListener) {
            //evento executado ao redimencionar a janela
            window.addEventListener('resize.corrigir_padding_conteudo', corrigir_padding_conteudo, false);
            //evento executado ao sair da pagina/fechar a pagina ou janela
            window.addEventListener('beforeunload', antes_de_sair_da_pagina, false);
        } else {
            window.attachEvent('onbeforeunload', antes_de_sair_da_pagina);
            window.attachEvent('resize.corrigir_padding_conteudo', corrigir_padding_conteudo);
        }

    }

    function startCkEditor() {
        ckenabledElementIds.map(function (id_elemento) {
            CKEDITOR.replace(id_elemento, ckeditor_config);
            // vicula a funcao para controlar a ativacao/desativacao do botao salvar, no evento de quando ha mudancas no editor
            // CKEDITOR.instances[id_elemento].on('change', function () {
            //     ativarDesativarSalvar();
            // });
        });
        // ativarDesativarSalvar();
    }


    // configuracao das intancias do ckeditor
    var ckeditor_config = {
        extraPlugins: [
            'sharedspace',

            'autolink',
            'autogrow',
            "base64image",
            "dialog", // required by base64image
            "dialogui", // required by base64image
            "maiuscula",
            "extenso",
            'justify',
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
        startupShowBorders: false,
        autoGrow_onStartup: true,
        autoGrow_minHeight: 0,
        autoGrow_bottomSpace: 0,
        toolbar: 'Basic',
        toolbar_Basic: [
            {name: 'save', items: ['Inlinesave']},
            '/',
            {name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {name: 'editing', items: ['Scayt', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {name: 'links', items: ['Link', 'Unlink', 'Anchor']},
            {name: 'insert', items: ['base64image', 'Table', 'HorizontalRule', 'SpecialChar']},
            {name: 'extra', items: ['Extenso', "Maiuscula", "Minuscula"]},
            {name: 'document', items: ['Source']},
            '/',
            {
                name: 'basicstyles',
                items: ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']
            },
            {
                name: 'paragraph',
                items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote']
            },
            {name: 'styles', items: ['Styles', 'Format']},
            {name: 'about', items: ['About']}

        ],
        // desativa o Advanced Content Filter
        // http://docs.ckeditor.com/#!/guide/dev_advanced_content_filter
        // para poder utilizar o plugin stylesheetparser http://ckeditor.com/addon/stylesheetparser
        //allowedContent: true,
        // end desativa o Advanced Content Filter
        base64image_disableUrlImages: true,
        justifyClasses: ['AlignLeft', 'AlignCenter', 'AlignRight', 'AlignJustify']


    };

    function init_page_scripts() {
        register_windows_page_events();
        startCkEditor();

    }

    //
    // //http://brack3t.com/ajax-and-django-views.html
    // //https://github.com/wavded/humane-js
    // //https://github.com/alertifyjs/alertify.js
    // //versao 2
    // jQuery(document).ready(function () {
    //
    //
    //     var requestRunning = false;
    //
    //
    //     function clear_form_field_errors(form) {
    //         jQuery(".ajax-error", jQuery(form)).remove();
    //         jQuery(".error", jQuery(form)).removeClass("error");
    //     }
    //
    //     //seu codigo lindo aqui
    //     $formulario.submit(function (event) {
    //         // Stop form from submitting normally
    //         event.preventDefault();
    //
    //
    //         if (requestRunning) { // don't do anything if an AJAX request is pending
    //             return;
    //         }
    //
    //         for (var instance in CKEDITOR.instances) {
    //             if (CKEDITOR.instances.hasOwnProperty(instance)) {
    //                 //atualiza o textarea vinculado ao editor
    //                 //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-updateElement
    //                 CKEDITOR.instances[instance].updateElement();
    //             }
    //         }
    //         // Get some values from elements on the page:
    //         var $form = jQuery(this);
    //         var conteudo = $form.serializeArray();
    //         var url = $form.attr("action").replace(/\s/g, "");
    //
    //         clear_form_field_errors($form);
    //         requestRunning = true;
    //         // Send the data using post
    //         // parametros url, data, callback, type
    //         // sendo que callback é sucess
    //         var posting = $.post(url, conteudo, 'JSON');
    //
    //         // Put the results in a div
    //         posting.fail(function (jqXHR, textStatus, errorThrown) {
    //
    //
    //             var errors = jqXHR.responseJSON;
    //
    //             log_to_console(errors);
    //             var msg = "Erro ao salvar documento" + errors.document_number + "\n";
    //             humane.log(msg, {
    //                 timeout: 2500,
    //                 clickToClose: true,
    //                 addnCls: 'humane-error'
    //             });
    //
    //
    //         });
    //         // Put the results in a div
    //         posting.done(function (data, textStatus, jqXHR) {
    //             log_to_console("done data:", data);
    //             log_to_console("done textStatus:", textStatus);
    //             log_to_console("done jqXHR:", jqXHR);
    //             // var content = jQuery(data);
    //             log_to_console(jQuery(data));
    //             for (var editor_instance in CKEDITOR.instances) {
    //                 if (CKEDITOR.instances.hasOwnProperty(editor_instance)) {
    //                     // http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-resetDirty
    //                     CKEDITOR.instances[editor_instance].resetDirty();
    //                     //http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-resetUndo
    //                     CKEDITOR.instances[editor_instance].resetUndo();
    //
    //                     conteudo_modificado[editor_instance] = false;
    //                 }
    //             }
    //             ativarDesativarSalvar();
    //             var mensagem = "Documento N° " + data.document_number + " salvo com sucesso!";
    //             humane.log(mensagem, {
    //                 timeout: 2500,
    //                 clickToClose: true,
    //                 addnCls: 'humane-sucess'
    //             });
    //             $status_bar.empty().append('Documento: ' + data.identificador_versao);
    //         });
    //         posting.always(function (data, textStatus, errorThrown) {
    //             log_to_console("always");
    //             requestRunning = false;
    //         });
    //     }).bind('ajax:complete', function () {
    //
    //         // tasks to do
    //         log_to_console("ajax completo");
    //
    //
    //     });
    //     $botao_salvar.click(function () {
    //
    //         $formulario.submit();
    //
    //     });
    //
    //
    // });

    //inicia os scripts basicos da pagina
    init_page_scripts();

    //
    Pace.on('hide', function () {

        // $main_div.fadeIn("fast");
        corrigir_padding_conteudo();
        for (var instance in CKEDITOR.instances) {
            if (CKEDITOR.instances.hasOwnProperty(instance)) {
                //instance.editor.fire( 'click' );
                CKEDITOR.instances[instance].execCommand('autogrow');
            }

        }
    });


})(window, django.jQuery, Pace, humane, window.luzfcb || (window.luzfcb = {}));

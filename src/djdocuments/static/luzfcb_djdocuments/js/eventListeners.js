/**
 * Created by luzfcb on 11/04/17.
 * based on: https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */

// onde será colocado o contedo buscado por AJAX
(function () {


    var id_modal = 'autocreatedmodal';
    var m_template = "<div id=\"" + id_modal + "\"></div>";
    var the_modal = $(m_template);
    // inicializa a modal
    the_modal.iziModal({
        bodyOverflow: false,
        autoOpen: false
    });

    $("body").append(the_modal);
    var the_modal_body = $('.iziModal-content', the_modal);

    function dealWithIt(event) {
        // lê o cache
        the_modal.iziModal('startLoading');
        the_modal.iziModal('open');
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
                    the_modal_body.html($(documentFragment));
                    the_modal.iziModal('stopLoading');
                });
        } else {
            // se tivermos feito o prefetch quando o usuário clicar no link, buscar do cache
            the_modal_body.html($(cache.fragment));
            the_modal.iziModal('stopLoading');
        }


    }


    // seleciona os links que queremos rodar o AJAX no onclick
    $('a[luzfcbmodal]').each(function (index, el) {
        $(el).on('click', dealWithIt);
    });
})();

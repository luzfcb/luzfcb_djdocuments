/**
 * Created by luzfcb on 11/04/17.
 * https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */
(function (window, document) {
    var cache = {};
    var $head = undefined;
    var $body = undefined;

    function cacheContent(params) {
        console.log('iniciando cache');
        // cria um novo elemento e passa o conteúdo pro innerHTML para se fazer o parsing para DOM
        var documentFragment = document.createElement('div');
        documentFragment.innerHTML = params.response;

        // passa pro jQuery
        var $fragment = $(documentFragment);

        var $stylesheets = $fragment.find('link[rel="stylesheet"]');
        var $scripts = $fragment.find('script');

        // clona os estilos e scripts presentes e depois remove
        var stylesheets = $stylesheets.clone();
        var scripts = $scripts.clone();

        $stylesheets.remove();
        $scripts.remove();

        // cria um objeto no cache para acesso
        cache[params.id] = {
            fragment: $fragment,
            stylesheets: stylesheets,
            scripts: scripts,
        };

        $head.append(stylesheets);
        $body.append(scripts);

        // retorna o fragmento para caso queira trabalhar com ele por fora
        return $fragment;
    }

    function prefetch() {
        $head = $('head');
        $body = $('body');

        // seleciona todos os links marcados como <a rel="[prefetch]">
        var $linksToPrefetch = $('a[rel="prefetch"]');
        var $link = undefined;
        var linkId = undefined;
        var length = $linksToPrefetch.length - 1;

        for (var index = 0; index <= length; index++) {
            $link = $linksToPrefetch[index];
            linkId = $link.data('id');

            // verifica se já no markup não tenha um data-id passado
            if (typeof linkId === 'undefined') {
                // se não tiver, crie um ID único
                $link.data('id', 'prefetch_' + Math.random().toString().substr(2));
            }

            var url = $link.attr('href');
            fetchContent({url: url, linkId: linkId});
        }
    }

    window.getCache = function getCache(id) {
        // passando uma cópia do cache, por motivos de segurança
        return $.extend({}, cache[id]);
    };

    window.fetchContent = function fetchContent(params) {
        return $.ajax(params.url)
        // quando o ajax retornar, passa a resposta e o ID para a fn cacheContent
            .then(function (response) {
                cacheContent({response: response, id: params.linkId});
            });
    };

    document.onreadystatechange = function onReady() {
        if (document.readyState === 'complete') {
            prefetch();
        }
    };
})(window, document);

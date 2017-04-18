/**
 * Created by luzfcb on 11/04/17.
 * based on: https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */
(function (window, document) {
    'use strict';
    var cache = {};
    var $head = undefined;
    var $body = undefined;

    function cacheContent(params) {
        //console.log('iniciando cache, parametros sao:');
        //console.log(params);
        $head = $head || $('head');
        $body = $body || $('body');

        // cria um novo elemento e passa o conteúdo pro innerHTML para se fazer o parsing para DOM
        var documentFragment = document.createElement('div');
        documentFragment.innerHTML = params.response;

        // passa pro jQuery
        var $fragment = $(documentFragment);
        $fragment.attr('data-autocreated', true);

        var $stylesheets = $fragment.find('link[rel="stylesheet"]');
        var $scripts = $fragment.find('script');

        // clona os estilos e scripts presentes e depois remove
        var stylesheets = $stylesheets.clone();
        var scripts = $scripts.clone();

        $stylesheets.remove();
        $scripts.remove();

        stylesheets.attr('data-autocreated', true);
        scripts.attr('data-autocreated', true);
        // cria um objeto no cache para acesso
        cache[params.id] = {
            fragment: $fragment.html(),
            stylesheets: stylesheets,
            scripts: scripts
        };

        stylesheets.each(function (index, el) {
            var link_selector = 'link[href="' + el.getAttribute("href") + '"]';
            if ($(link_selector).length) {
                // ja existe
            } else {
                $head.append(el)
            }

        });
        scripts.each(function (index, el) {
            var link_selector = 'script[src="' + el.getAttribute("src") + '"]';
            if ($(link_selector).length) {
                // ja existe
            } else {
                $body.append(el)
            }

        });

        // retorna o fragmento para caso queira trabalhar com ele por fora
        return $fragment.html();
    }

    function prefetch() {
        //console.log('executando prefetch()');
        $head = $('head');
        $body = $('body');

        // seleciona todos os links marcados como <a rel="[prefetch]">
        var $linksToPrefetch = $('a[rel="prefetch"]');
        var $link = undefined;
        var linkId = undefined;
        var length = $linksToPrefetch.length - 1;

        for (var index = 0; index <= length; index++) {
            $link = $($linksToPrefetch[index]);
            linkId = $link.data('id');


            // verifica se já no markup não tenha um data-id passado
            if (typeof linkId === 'undefined') {
                // se não tiver, crie um ID único
                linkId = 'prefetch_' + getUUID();
                $link.attr('data-id', linkId);
            }

            var url = $link.attr('href');
            fetchContent({url: url, linkId: linkId});
        }
    }

    window.getCache = function getCache(id) {

        if (!cache.hasOwnProperty(id)) {
            return undefined;
        }
        // passando uma cópia do cache, por motivos de segurança
        return $.extend({}, cache[id]);
    };

    window.fetchContent = function fetchContent(params) {
        //console.log('executando fetchContent');
        return $.ajax(params.url)
        // quando o ajax retornar, passa a resposta e o ID para a fn cacheContent
            .then(function (response) {
                //console.log('ajax reponse do linkId: ' + params.linkId + '\n');
                //console.log(response);
                //console.log('\n\n');
                return cacheContent({response: response, id: params.linkId});

            });
    };
    // executa previamente o ajax, logo apos toda a pagina tiver sido carregada.
    document.onreadystatechange = function onReady() {
        if (document.readyState === 'complete') {
            prefetch();
        }
    };
    window.getOrAndApplyId = function getIdOrCreateAndApplyId(el) {
        var self = $(el);
        var id_ = self.data('id');
        //console.log(id_);
        if (typeof id_ === "undefined") {
            //console.log('gerou novo em getOrAndApplyId');
            id_ = getUUID();
            self.attr('data-id', id_);
        }
        return id_;
    };
    window.getUUID = (function () {
        //"e" function of https://jsperf.com/node-uuid-performance/62
        var d;
        if (window.crypto && crypto.getRandomValues) {
            var e = new Uint8Array(16);
            d = function () {
                crypto.getRandomValues(e);
                return e
            }
        }
        window.msCrypto && msCrypto.getRandomValues && (e = new Uint8Array(16), d = function () {
            msCrypto.getRandomValues(e);
            return e
        });
        if (!d) {
            var g = Array(16);
            d = function () {
                for (var b = 0,
                         a; 16 > b; b++)0 === (b & 3) && (a = 4294967296 * Math.random()), g[b] = a >>> ((b & 3) << 3) & 255;
                return g
            }
        }
        for (var c = [], f = 0; 256 > f; f++)c[f] = (f + 256).toString(16).substr(1);
        return function () {
            var b = 0, a = d();
            a[6] = a[6] & 15 | 64;
            a[8] = a[8] &
                63 | 128;
            return c[a[b++]] + c[a[b++]] + c[a[b++]] + c[a[b++]] + "-" + c[a[b++]] + c[a[b++]] + "-" + c[a[b++]] + c[a[b++]] + "-" + c[a[b++]] + c[a[b++]] + "-" + c[a[b++]] + c[a[b++]] + c[a[b++]] + c[a[b++]] + c[a[b++]] + c[a[b++]]
        }
    })();
})(window, document);

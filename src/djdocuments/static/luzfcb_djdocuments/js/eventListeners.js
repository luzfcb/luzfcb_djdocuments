/**
 * Created by luzfcb on 11/04/17.
 * https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */

// onde será colocado o contedo buscado por AJAX
var $whereToPutIt = $('.where-to-put-it');

function dealWithIt(event) {
    console.log('executou o click');
    // lê o cache
    var id_ = $(this).data('id');
    var cache = getCache(id_);

    event.preventDefault();

    if (typeof cache === 'undefined') {
        // se quando o usurio clicar no link ainda não tiver sido feito o prefetch do conteúdo,
        // executar o fetch no ato.
        fetchContent({url: this.attr('href'), linkId: this.data('id')})
            .then(function (fragment) {
                $whereToPutIt.append(fragment);
            });
    } else {
        // se tivermos feito o prefetch quando o usário clicar no link, buscar do cache
        $whereToPutIt.append(cache.fragment);
    }
}

// seleciona os links que queremos rodar o AJAX no onclick
$('a.blah').on('click', dealWithIt);

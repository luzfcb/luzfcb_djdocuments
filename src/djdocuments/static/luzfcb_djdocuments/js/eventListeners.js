/**
 * Created by luzfcb on 11/04/17.
 * https://gist.github.com/WebCloud/906429ae3689b280b84583a5718ba708
 */

// onde será colocado o contedo buscado por AJAX
var $whereToPutIt = $('#inseriraqui');
var modal_template = "<div>";
modal_template += "<div id=\"mymodal\" class=\"modal hide fade\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"myModalLabel\" aria-hidden=\"true\">";
modal_template += "  <div class=\"modal-header\">";
modal_template += "    <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">&times;<\/button>";
modal_template += "  <\/div>";
modal_template += "  <div class=\"modal-body\">";
modal_template += "  <\/div>";
modal_template += "  <div class=\"modal-footer\">";
modal_template += "  <\/div>";
modal_template += "<\/div><\/div>";


function dealWithIt(event) {
    console.log('executou o click');
    // lê o cache
    var id_ = getOrAndApplyId(this);
    var cache = getCache(id_);
    console.log('id_: ' + id_);
    console.log('cache: ');
    console.log(cache);
    event.preventDefault();

    $('body > #inseriraqui').html($(modal_template).html());
    var mymodal = $('#mymodal');
    var mymodal_body = $('.modal-body', mymodal);
    if (typeof cache === 'undefined') {
        // se quando o usuario clicar no link ainda não tiver sido feito o prefetch do conteúdo,
        // executar o fetch no ato.
        var self = $(this);
        console.log('cache nao existe, criando novo cache');
        fetchContent({url: self.attr('href'), linkId: self.data('id')})
            .then(function (fragment) {
                console.log('executou fetchContent');
                console.log('fragment: ' + fragment);
                // $whereToPutIt.append($(fragment));
                var documentFragment = document.createElement('div');
                documentFragment.innerHTML = fragment;
                // $(documentFragment).hide();
                mymodal_body.append($(documentFragment));
            });
    } else {
        console.log('cache existe, e o fragmento é: \n');
        console.log(cache.fragment);
        // se tivermos feito o prefetch quando o usário clicar no link, buscar do cache
        // $whereToPutIt.append($(cache.fragment));
        mymodal_body.append($(cache.fragment));
    }

    mymodal.modal('show');
}


// seleciona os links que queremos rodar o AJAX no onclick
$('a[luzfcbmodal]').on('click', dealWithIt);

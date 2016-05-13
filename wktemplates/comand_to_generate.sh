./wkhtmltopdf --encoding utf8 --footer-html rodape.html --header-html cabecalho.html --margin-bottom 0mm --margin-left 0mm --margin-right 0mm --margin-top 0mm --page-size A4 --print-media-type --quiet corpo.html

wkhtmltopdf --encoding utf8 --footer-html footer.html --header-html header.html --margin-bottom 0mm --margin-left 0mm --margin-right 0mm --margin-top 0mm --page-size A4 --print-media-type --quiet content.html output_with_header_and_footer.pdf

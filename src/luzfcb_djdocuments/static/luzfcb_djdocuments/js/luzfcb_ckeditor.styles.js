/**
 * Created by luzfcb on 04/03/16.
 */
if (typeof(CKEDITOR) !== 'undefined') {
// The set of styles for the <b>Styles</b> drop-down list.
    CKEDITOR.stylesSet.add('luzfcb_djdocuments', [
        // Block Styles
        {name: 'Blue Title', element: 'h3', styles: {'color': 'Blue'}},
        {name: 'Red Title', element: 'h3', styles: {'color': 'Red'}},

        // // Inline Styles
        // {name: 'Marker: Yellow', element: 'span', styles: {'background-color': 'Yellow'}},
        // {name: 'Marker: Green', element: 'span', styles: {'background-color': 'Lime'}},
        //
        // // Object Styles
        // {
        //     name: 'Imagem a esquerda',
        //     element: 'img',
        //     attributes: {
        //         style: 'padding: 5px; margin-right: 5px',
        //         border: '2',
        //         align: 'left'
        //     }
        // },
        // {
        //     name: 'Imagem a direita2',
        //     element: 'img',
        //     // attributes: {
        //     styles: 'padding: 5px; margin-right: 5px; border: 2; align: right',
        //     // border: '2',
        //     // align: 'right'
        //     // }
        // },
        // {
        //     name: 'Imagem a centro',
        //     element: 'img',
        //     attributes: {
        //         style: 'padding: 5px; margin-right: 5px',
        //         border: '2',
        //         align: 'middle'
        //     }
        // },
        {
            name: 'Imagem Centralizar',
            element: 'img',
            attributes: {
                class: 'img-responsive center-block'
            }
        },
        {
            name: 'Imagem Esquerda',
            element: 'img',
            attributes: {
                class: 'img-responsive pull-left'
            }
        },
        {
            name: 'Imagem Direita',
            element: 'img',
            attributes: {
                class: 'img-responsive pull-right'
            }
        }
    ]);
}

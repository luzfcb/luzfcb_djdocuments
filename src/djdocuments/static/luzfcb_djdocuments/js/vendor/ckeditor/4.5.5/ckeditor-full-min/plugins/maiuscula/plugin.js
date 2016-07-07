﻿CKEDITOR.plugins.add("maiuscula", {
	init: function (a) {
		a.addCommand("alterarMaiuscula", {
			exec: function (b) {
				var a = b.getSelection().getSelectedText();
				b.insertHtml(a.toUpperCase())
			}
		});
		a.addCommand("alterarMinuscula", {
			exec: function (a) {
				var c = a.getSelection().getSelectedText();
				a.insertHtml(c.toLowerCase())
			}
		});
		a.ui.addButton("Maiuscula", {
			label: "Altera o texto para MAIÚSCULAS",
			command: "alterarMaiuscula",
			icon: this.path + "images/maiusculas.gif"
		});
		a.ui.addButton("Minuscula", {
			label: "Altera o texto para minúsculas",
			command: "alterarMinuscula", icon: this.path + "images/minusculas.gif"
		})
	}
});
CKEDITOR.plugins.add("extenso", {
	init: function (j) {
		j.addCommand("inserirExtenso", {
			exec: function (j) {

				var utilRTrim = function (String) {
					if (String != null && String.length > 0) {
						while (String.charAt((String.length - 1)) == ' ') {
							String = String.substring(0, String.length - 1);
						}
					}
					return String;
				};

				var utilLTrim = function (String) {
					if (String != null && String.length > 0) {
						while (String.charAt(0) == ' ') {
							String = String.replace(String.charAt(0), '');
						}
					}
					return String;
				};

				var utilTrim = function (String) {
					String = utilLTrim(String);
					return utilRTrim(String);
				};

				var validateMoneyFormat = function (din) {
					var regex_money = /^(R\$[ ]*)?[0-9]{1,3}(?:.?[0-9]{3})*(?:,[0-9]{2})?$/;
					return regex_money.test(utilTrim(din));
				};

				var k = j.getSelection().getSelectedText();
				if (validateMoneyFormat(k)) {
					var g = ["zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove".split(" "), "dez vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split(" "), "cem cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split(" "), "mil milhão bilhão trilhão quadrilhão quintilhão sextilhão setilhão octilhão nonilhão decilhão undecilhão dodecilhão tredecilhão quatrodecilhão quindecilhão sedecilhão septendecilhão octencilhão nonencilhão".split(" ")],
						c, h, a, b;
					h = k.replace(/[^,\d]/g, "").split(",");
					for (var m = h.length - 1, e, f = -1, l = [], i = [], d = ""; ++f <= m; i = [])if (f && (h[f] = (1 * ("." + h[f])).toFixed(2).slice(2)), (c = (a = h[f]).slice((e = a.length) % 3).match(/\d{3}/g), a = e % 3 ? [a.slice(0, e % 3)] : [], a = c ? a.concat(c) : a).length) {
						c = -1;
						for (e = a.length; ++c < e; d = "")if (b = 1 * a[c])20 > b % 100 && (d += g[0][b % 100]) || b % 100 + 1 && (d += g[1][(b % 100 / 10 >> 0) - 1] + (b % 10 ? " e " + g[0][b % 10] : "")), i.push((100 > b ? d : !(b % 100) ? g[2][100 == b ? 0 : b / 100 >> 0] : g[2][b / 100 >> 0] + " e " + d) + (-1 < (d = e - c - 2) ? " " + (1 < b && 0 < d ? g[3][d].replace("ão",
								"ões") : g[3][d]) : ""));
						0 == 1 * a[e - 1] % 100 && 0 < 1 * a[e - 1] ? e2 = " e " : 1 < e && 0 == 1 * a[e - 2] ? e2 = ", " : e2 = " ";
						(c = 1 < i.length ? (c = i.pop(), i.join(", ") + e2 + c) : i.join("") || (!f && 0 < 1 * h[f + 1] || l.length ? "" : g[0][0])) && l.push(c + " " + (1 < 1 * a.join("") ? f ? "centavos" : (/0{6,}$/.test(h[0]) ? "de " : "") + "real".replace("l", "is") : f ? "centavo" : "real"))
					}
					j.insertHtml(k + " (" + l.join(" e ") + ")")
				} else 0 == k.trim().length ? alert("Selecione o número para preencher por extenso. Use . para separar milhar e , para casas decimais.") : alert("Número inválido, selecione um número.")
			}
		});
		j.ui.addButton("Extenso", {
			label: "Inserir valor monetário por extenso",
			command: "inserirExtenso",
			icon: this.path + "images/extenso.png"
		})
	}
});

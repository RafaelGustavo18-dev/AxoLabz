/* AxoLabz — formulários. Nada é enviado nem guardado: os dados só viram texto de WhatsApp
   quando a pessoa confirma. Sem localStorage, sessionStorage ou cookies. */
(function () {
  "use strict";
  var A = window.AXO;
  if (!A) return;
  var C = A.config;
  var params = new URLSearchParams(location.search);

  function val(f, n) { var e = f.elements[n]; return e && e.value ? e.value.trim() : ""; }
  function checked(f, n) {
    return Array.prototype.map.call(f.querySelectorAll("input[name=" + n + "]:checked"), function (i) {
      return i.getAttribute("data-label") || i.value;
    });
  }
  function firstId(f, n) { var e = f.querySelector("[name=" + n + "]"); return e ? e.id : n; }
  function normLink(s) {
    s = (s || "").trim();
    if (s && !/^https?:\/\//i.test(s)) s = "https://" + s;
    return s;
  }
  function googleLink(s) {
    try {
      var u = new URL(s);
      if (u.protocol !== "https:") return false;
      return /(^|\.)(google\.com|g\.page|goo\.gl|g\.co)$/.test(u.hostname);
    } catch (e) { return false; }
  }

  var SPECS = {
    digital: {
      intro: "Olá, AxoLabz! Gostaria de solicitar um orçamento.",
      outro: "Entendo que escopo, preço, prazo e condições de pagamento serão confirmados pela AxoLabz antes de qualquer início de trabalho.",
      validate: function (f) {
        var e = [];
        if (!f.querySelector("input[name=tipo]:checked") && !f.elements.orientacao.checked)
          e.push({ id: firstId(f, "tipo"), err: "err-tipo", msg: "Escolha o tipo de projeto ou marque que precisa de orientação." });
        if (!val(f, "negocio"))
          e.push({ id: "negocio", err: "err-negocio", msg: "Informe o nome do negócio." });
        var p = val(f, "paginas");
        if (p && !(/^\d+$/.test(p) && +p >= 1 && +p <= 50))
          e.push({ id: "paginas", err: "err-paginas", msg: "Use um número inteiro de páginas entre 1 e 50." });
        return e;
      },
      pairs: function (f) {
        var t = f.querySelector("input[name=tipo]:checked");
        return [
          ["Tipo de projeto", t ? t.getAttribute("data-label") : ""],
          ["Negócio", val(f, "negocio")],
          ["Páginas desejadas", val(f, "paginas")],
          ["Funcionalidades", checked(f, "func").join(", ")],
          ["Orientação", f.elements.orientacao.checked ? "Preciso de ajuda para escolher a solução" : ""],
          ["Observações", val(f, "obs")]
        ];
      }
    },
    pedido: {
      intro: "Olá, AxoLabz! Quero solicitar uma placa de avaliação do Google.",
      outro: "Entendo que preço, prazo, disponibilidade e condições de pagamento serão confirmados pela AxoLabz, e que o pedido só vale após essa confirmação.",
      validate: function (f) {
        var e = [];
        if (!f.querySelector("input[name=variante]:checked"))
          e.push({ id: firstId(f, "variante"), err: "err-variante", msg: "Escolha uma das quatro variantes: tamanho e cor." });
        if (!val(f, "estab"))
          e.push({ id: "estab", err: "err-estab", msg: "Informe o nome do estabelecimento." });
        var l = normLink(val(f, "link"));
        if (!l) e.push({ id: "link", err: "err-link", msg: "Cole o link de avaliação do Google do seu estabelecimento." });
        else if (!googleLink(l)) e.push({ id: "link", err: "err-link", msg: "Esse link não parece ser do Google. Use o link de avaliação, como https://g.page/r/..." });
        return e;
      },
      pairs: function (f) {
        var v = f.querySelector("input[name=variante]:checked");
        return [
          ["Produto", "Placa de avaliação do Google"],
          ["Tamanho", v ? v.getAttribute("data-size") : ""],
          ["Cor", v ? v.getAttribute("data-color") : ""],
          ["NFC", "Incluso"],
          ["QR Code adicional", f.elements.qr.checked ? "Sim, quero o QR Code adicional" : "Não"],
          ["Estabelecimento", val(f, "estab")],
          ["Link de avaliação", normLink(val(f, "link"))],
          ["Observações", val(f, "obs")]
        ];
      }
    }
  };

  document.querySelectorAll("form[data-form]").forEach(init);

  function init(f) {
    var spec = SPECS[f.getAttribute("data-form")];
    var summary = f.querySelector(".err-summary");
    var review = f.nextElementSibling;
    if (!spec || !summary || !review) return;

    prefill(f);
    if (f.getAttribute("data-form") === "pedido") product(f);

    f.addEventListener("input", function (ev) {
      var n = ev.target.name, s = n && document.getElementById("err-" + n);
      if (s && s.textContent) {
        s.textContent = "";
        (ev.target.type === "radio" ? ev.target.closest("fieldset") : ev.target).removeAttribute("aria-invalid");
      }
    });

    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      f.querySelectorAll(".err").forEach(function (s) { s.textContent = ""; });
      f.querySelectorAll("[aria-invalid]").forEach(function (x) { x.removeAttribute("aria-invalid"); });
      var errs = spec.validate(f);
      if (errs.length) return showErrors(f, summary, errs);
      summary.hidden = true;
      showReview(f, review, spec);
    });
  }

  function showErrors(f, summary, errs) {
    summary.innerHTML = "";
    var h = document.createElement("h2");
    h.textContent = errs.length === 1 ? "Há 1 campo para corrigir" : "Há " + errs.length + " campos para corrigir";
    var ul = document.createElement("ul");
    errs.forEach(function (er) {
      var el = document.getElementById(er.id);
      document.getElementById(er.err).textContent = er.msg;
      var mark = el && el.type === "radio" ? el.closest("fieldset") : el;
      if (mark) mark.setAttribute("aria-invalid", "true");
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = "#" + er.id;
      a.textContent = er.msg;
      a.addEventListener("click", function (e) { e.preventDefault(); if (el) el.focus(); });
      li.appendChild(a);
      ul.appendChild(li);
    });
    summary.appendChild(h);
    summary.appendChild(ul);
    summary.hidden = false;
    summary.focus();
    summary.scrollIntoView({ block: "center" });
  }

  function showReview(f, r, spec) {
    var prs = spec.pairs(f).filter(function (p) { return p[1]; });
    var msg = spec.intro + "\n\n" +
      prs.map(function (p) { return "*" + p[0] + ":* " + p[1]; }).join("\n") +
      "\n\n" + spec.outro;

    r.innerHTML =
      '<h2 id="rev-title" tabindex="-1">Revise antes de abrir o WhatsApp</h2>' +
      '<dl class="rev-list"></dl>' +
      '<label class="lab" for="msg-copy">Mensagem preparada</label>' +
      '<textarea id="msg-copy" readonly rows="10"></textarea>' +
      '<div class="notice"><p><strong>Isto ainda não é um pedido confirmado.</strong> Nada foi enviado. Ao abrir o WhatsApp, você segue para um serviço externo e só envia se quiser. Preço, prazo, disponibilidade e condições de pagamento serão confirmados pela AxoLabz.</p></div>' +
      '<div class="notice warn" id="rev-nowa" hidden><p><strong>O WhatsApp da AxoLabz ainda não foi configurado neste site.</strong> Copie a mensagem acima e envie manualmente quando tiver o contato.</p></div>' +
      '<div class="opt"><input type="checkbox" id="rev-ok"><label for="rev-ok">Revisei as informações e quero abrir o WhatsApp.</label></div>' +
      '<p class="err" id="err-rev" role="alert"></p>' +
      '<div class="actions"><button type="button" class="btn" id="rev-open">Abrir WhatsApp</button>' +
      '<button type="button" class="btn line" id="rev-copy">Copiar mensagem</button>' +
      '<button type="button" class="btn line" id="rev-back">Voltar e editar</button></div>' +
      '<p class="status" id="rev-status" role="status"></p>';

    var dl = r.querySelector(".rev-list");
    prs.forEach(function (p) {
      var dt = document.createElement("dt"), dd = document.createElement("dd");
      dt.textContent = p[0];
      dd.textContent = p[1];
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    var ta = r.querySelector("#msg-copy");
    ta.value = msg;

    var link = A.waLink(msg);
    var open = r.querySelector("#rev-open"), ok = r.querySelector("#rev-ok"), er = r.querySelector("#err-rev");
    if (!link) {
      r.querySelector("#rev-nowa").hidden = false;
      open.disabled = true;
      ok.disabled = true;
    }
    open.addEventListener("click", function () {
      if (!link) return;
      if (!ok.checked) {
        er.textContent = "Marque a confirmação para abrir o WhatsApp.";
        ok.focus();
        return;
      }
      window.location.href = link;
    });
    ok.addEventListener("change", function () { if (ok.checked) er.textContent = ""; });
    r.querySelector("#rev-copy").addEventListener("click", function () {
      var done = function () { r.querySelector("#rev-status").textContent = "Mensagem copiada."; };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(msg).then(done, function () { fallback(); });
      } else fallback();
      function fallback() {
        ta.select();
        try { document.execCommand("copy"); done(); }
        catch (e) { r.querySelector("#rev-status").textContent = "Não foi possível copiar. Selecione o texto e copie manualmente."; }
      }
    });
    r.querySelector("#rev-back").addEventListener("click", function () {
      r.hidden = true;
      f.hidden = false;
      var first = f.querySelector("input:not([type=radio]):not([type=checkbox]),textarea");
      if (first) first.focus();
    });

    f.hidden = true;
    r.hidden = false;
    var t = r.querySelector("#rev-title");
    t.focus();
    t.scrollIntoView({ block: "start" });
  }

  function prefill(f) {
    var tipo = params.get("tipo");
    if (f.getAttribute("data-form") === "digital" && tipo) {
      var r = f.querySelector('input[name=tipo][value="' + tipo.replace(/[^\w-]/g, "") + '"]');
      if (r) r.checked = true;
      else if (tipo === "manutencao" || tipo === "orientacao") {
        f.elements.orientacao.checked = true;
        if (tipo === "manutencao" && !f.elements.obs.value)
          f.elements.obs.value = "Tenho interesse no serviço opcional de manutenção.";
      }
    }
    var v = params.get("v");
    if (f.getAttribute("data-form") === "pedido") {
      if (v) {
        var rv = f.querySelector('input[name=variante][value="' + v.replace(/[^\w-]/g, "") + '"]');
        if (rv) rv.checked = true;
      }
      var notes = [];
      if (params.get("customLogo") === "1") notes.push("Quero incluir meu logo personalizado; vou enviar o arquivo pelo WhatsApp.");
      if (params.has("customQr")) {
        var wantsQr = params.get("customQr") === "1";
        if (f.elements.qr) f.elements.qr.checked = wantsQr;
      }
      if (params.get("customQr") === "1") {
        notes.push("Quero incluir QR Code na placa; vou enviar a imagem pelo WhatsApp se já tiver uma.");
      }
      if (notes.length && f.elements.obs && !f.elements.obs.value.trim()) f.elements.obs.value = notes.join(" ");
    }
  }

  // Página do produto: mostra arte, preço e dimensões da variante escolhida.
  function product(f) {
    function update() {
      var sel = f.querySelector("input[name=variante]:checked");
      document.querySelectorAll("[data-variant-art]").forEach(function (el) {
        el.hidden = el.getAttribute("data-variant-art") !== (sel ? sel.value : "M-branca");
      });
      var size = sel ? sel.getAttribute("data-size") : null;
      var price = document.getElementById("plate-price"), chosen = document.getElementById("chosen");
      var dim = document.getElementById("plate-dim");
      if (chosen) chosen.textContent = sel ? "Tamanho " + size + ", cor " + sel.getAttribute("data-color").toLowerCase() : "Escolha uma variante";
      if (price) {
        var p = size ? A.money(((C.plates || {})[size] || {}).price) : null;
        price.textContent = !size ? "Escolha o tamanho para ver o preço" : (p ? p + " (NFC incluso)" : "Preço sob consulta: será confirmado pelo WhatsApp");
      }
      if (dim) {
        var d = size && ((C.plates || {})[size] || {}).dimensions;
        dim.textContent = typeof d === "string" && d.trim() ? d.trim() : "A confirmar";
      }
    }
    f.addEventListener("change", update);
    update();
    var q = document.getElementById("qr-price");
    if (q) q.textContent = A.money(C.qrAddonPrice) || "Valor a confirmar";
  }
})();

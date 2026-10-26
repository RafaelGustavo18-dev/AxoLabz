/* AxoLabz — comportamento geral. Os dados comerciais vêm de config.js. */
(function () {
  "use strict";
  var C = window.AXO_CONFIG || {};
  var root = document.body.getAttribute("data-root") || "";

  var num = String(C.whatsapp || "").replace(/\D/g, "");
  if (num.length === 10 || num.length === 11) num = "55" + num;
  var waOk = /^\d{12,15}$/.test(num);

  var ig = null;
  try {
    var u = new URL(C.instagram || "");
    if (u.protocol === "https:" && /(^|\.)instagram\.com$/.test(u.hostname)) ig = u.href;
  } catch (e) {}

  function money(v) {
    return typeof v === "number" && isFinite(v) && v > 0
      ? v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
      : null;
  }

  window.AXO = {
    config: C,
    waOk: waOk,
    money: money,
    waLink: function (msg) {
      return waOk ? "https://wa.me/" + num + "?text=" + encodeURIComponent(msg) : null;
    }
  };

  function each(sel, fn) {
    Array.prototype.forEach.call(document.querySelectorAll(sel), fn);
  }

  // Links de WhatsApp: só abrem quando o número é válido; senão levam à página de contato com aviso.
  each("[data-wa]", function (a) {
    var msg = a.getAttribute("data-msg") || "Olá, AxoLabz! Gostaria de conversar sobre um projeto.";
    a.href = waOk ? window.AXO.waLink(msg) : root + "contato.html#aviso-whatsapp";
  });
  if (!waOk) {
    each(".wa-float,[data-wa-item]", function (el) { el.remove(); });
    each("[data-if-no-wa]", function (el) { el.hidden = false; });
  }
  if (ig) {
    each("[data-ig]", function (a) { a.href = ig; });
  } else {
    each("[data-ig-item]", function (el) { el.remove(); });
    each("[data-if-no-ig]", function (el) { el.hidden = false; });
  }

  var city = typeof C.city === "string" ? C.city.trim() : "";
  each("[data-city]", function (el) {
    if (city) el.textContent = (el.getAttribute("data-prefix") || "") + city; else el.remove();
  });
  each("[data-year]", function (el) { el.textContent = new Date().getFullYear(); });

  // Preços
  each("[data-price]", function (el) {
    var p = el.getAttribute("data-price").split(":");
    var v = null, text;
    if (p[0] === "digital") {
      v = money((C.digitalPrices || {})[p[1]]);
      text = v ? "A partir de " + v : (el.getAttribute("data-pending") || "Valor a confirmar");
    } else if (p[0] === "plate") {
      v = money(((C.plates || {})[p[1]] || {}).price);
      text = v ? v : "Preço sob consulta";
    } else if (p[0] === "qr") {
      v = money(C.qrAddonPrice);
      text = v ? v : "Valor a confirmar";
    }
    el.textContent = text;
  });
  each("[data-dim]", function (el) {
    var d = ((C.plates || {})[el.getAttribute("data-dim")] || {}).dimensions;
    if (typeof d === "string" && d.trim()) el.textContent = d.trim();
  });

  // Fotos reais substituem a ilustração só quando o arquivo carrega.
  each("[data-photo]", function (el) {
    var s = (C.photos || {})[el.getAttribute("data-photo")];
    if (typeof s === "string" && /^[\w\-./]+\.(jpe?g|png|webp|avif)$/i.test(s)) {
      var img = new Image();
      img.alt = el.getAttribute("data-alt") || "Placa AxoLabz";
      img.onload = function () {
        el.replaceChildren(img);
        var cap = (el.closest("figure,.stage,.studio") || el.parentNode).querySelector("[data-illus]");
        if (cap) cap.remove();
      };
      img.src = root + s;
    }
  });

  // Menu móvel
  var head = document.querySelector(".site-head");
  var btn = document.getElementById("menu-btn");
  if (head && btn) {
    btn.addEventListener("click", function () {
      var open = head.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && head.classList.contains("open")) {
        head.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  }

  // Botão flutuante some quando o visitante está preenchendo um campo
  var fl = document.querySelector(".wa-float");
  if (fl) {
    document.addEventListener("focusin", function (e) {
      fl.classList.toggle("hide", /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName));
    });
  }

  // Linha do processo
  var steps = document.querySelectorAll(".steps");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.3 });
    Array.prototype.forEach.call(steps, function (s) { io.observe(s); });
  } else {
    Array.prototype.forEach.call(steps, function (s) { s.classList.add("in"); });
  }
})();

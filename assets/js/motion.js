/* AxoLabz · interações leves, acessíveis e sem dependências externas */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  // Seletor da placa e prévia local das personalizações no configurador 3D.
  var viewer = document.querySelector("[data-product-viewer]");
  if (viewer) {
    var size = "G", color = "preta";
    var options = Array.prototype.slice.call(viewer.querySelectorAll("[data-plate-option]"));
    var sizeButtons = Array.prototype.slice.call(viewer.querySelectorAll("[data-plate-size]"));
    var colorButtons = Array.prototype.slice.call(viewer.querySelectorAll("[data-plate-color]"));
    var status = viewer.querySelector("[data-variant-status]");
    var orderLink = viewer.querySelector("[data-order-variant]");
    var logoInput = viewer.querySelector('[data-custom-file="logo"]');
    var qrInput = viewer.querySelector('[data-custom-file="qr"]');
    var qrToggle = viewer.querySelector("[data-preview-qr-toggle]");
    var customStatus = viewer.querySelector("[data-custom-status]");
    var custom = { logo: null, qr: null };

    function updateOrderLink() {
      if (!orderLink) return;
      var key = size + "-" + color;
      var href = "produtos/placa-avaliacao-google.html?v=" + encodeURIComponent(key);
      if (custom.logo) href += "&customLogo=1";
      href += "&customQr=" + ((qrToggle ? qrToggle.checked : true) ? "1" : "0");
      orderLink.href = href + "#pedido";
      orderLink.setAttribute("aria-label", "Pedir placa " + size + " " + (color === "preta" ? "preta" : "branca"));
    }

    function updateCustomPreview() {
      var hasLogo = !!custom.logo;
      var showQr = qrToggle ? qrToggle.checked : true;
      viewer.querySelectorAll("[data-plate-default-copy]").forEach(function (el) { el.style.display = hasLogo ? "none" : ""; });
      viewer.querySelectorAll("[data-plate-logo]").forEach(function (el) {
        if (custom.logo) el.setAttribute("href", custom.logo);
        else el.removeAttribute("href");
        el.style.display = hasLogo ? "inline" : "none";
      });
      viewer.querySelectorAll("[data-plate-qr-placeholder]").forEach(function (el) { el.style.display = showQr && !custom.qr ? "inline" : "none"; });
      viewer.querySelectorAll("[data-plate-qr-bg]").forEach(function (el) { el.style.display = showQr && !!custom.qr ? "inline" : "none"; });
      viewer.querySelectorAll("[data-plate-qr]").forEach(function (el) {
        if (custom.qr) el.setAttribute("href", custom.qr);
        else el.removeAttribute("href");
        el.style.display = showQr && !!custom.qr ? "inline" : "none";
      });
      viewer.querySelectorAll("[data-plate-nfc-right]").forEach(function (el) { el.style.display = showQr ? "" : "none"; });
      viewer.querySelectorAll("[data-plate-nfc-center]").forEach(function (el) { el.style.display = showQr ? "none" : ""; });
      updateOrderLink();
    }

    function showVariant() {
      var key = size + "-" + color;
      options.forEach(function (item) {
        var active = item.getAttribute("data-plate-option") === key;
        item.hidden = !active;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-hidden", active ? "false" : "true");
      });
      sizeButtons.forEach(function (button) {
        button.setAttribute("aria-pressed", button.getAttribute("data-plate-size") === size ? "true" : "false");
      });
      colorButtons.forEach(function (button) {
        button.setAttribute("aria-pressed", button.getAttribute("data-plate-color") === color ? "true" : "false");
      });
      var sizeText = viewer.querySelector("[data-selected-size]");
      var colorText = viewer.querySelector("[data-selected-color]");
      if (sizeText) sizeText.textContent = size;
      if (colorText) colorText.textContent = color === "preta" ? "Preta" : "Branca";
      updateOrderLink();
      if (status) status.textContent = "Prévia atualizada: placa " + size + " " + color + ".";
    }

    function readCustomFile(input, kind) {
      if (!input) return;
      input.addEventListener("change", function () {
        var file = input.files && input.files[0];
        if (!file) return;
        var label = viewer.querySelector('[data-custom-name="' + kind + '"]');
        var clear = viewer.querySelector('[data-clear-custom="' + kind + '"]');
        var allowed = /^image\/(png|jpeg|webp|svg\+xml)$/i.test(file.type) || /\.(png|jpe?g|webp|svg)$/i.test(file.name);
        if (!allowed || file.size > 5 * 1024 * 1024) {
          input.value = "";
          if (customStatus) customStatus.textContent = !allowed ? "Escolha uma imagem PNG, JPG, WEBP ou SVG." : "A imagem precisa ter até 5 MB.";
          return;
        }
        var reader = new FileReader();
        reader.onload = function () {
          var image = new Image();
          image.onload = function () {
            custom[kind] = String(reader.result);
            if (kind === "qr" && qrToggle) qrToggle.checked = true;
            if (label) label.textContent = file.name;
            if (clear) clear.hidden = false;
            if (customStatus) customStatus.textContent = (kind === "logo" ? "Logo" : "QR Code") + " aplicado à prévia.";
            updateCustomPreview();
          };
          image.onerror = function () {
            input.value = "";
            if (customStatus) customStatus.textContent = "Não foi possível abrir essa imagem. Tente outro arquivo.";
          };
          image.src = String(reader.result);
        };
        reader.onerror = function () {
          if (customStatus) customStatus.textContent = "Não foi possível ler essa imagem. Tente outro arquivo.";
        };
        reader.readAsDataURL(file);
      });
    }

    readCustomFile(logoInput, "logo");
    readCustomFile(qrInput, "qr");
    viewer.querySelectorAll("[data-clear-custom]").forEach(function (button) {
      button.addEventListener("click", function () {
        var kind = button.getAttribute("data-clear-custom");
        var input = kind === "logo" ? logoInput : qrInput;
        if (input) input.value = "";
        custom[kind] = null;
        var label = viewer.querySelector('[data-custom-name="' + kind + '"]');
        if (label) label.textContent = "PNG, JPG, WEBP ou SVG · até 5 MB";
        button.hidden = true;
        if (customStatus) customStatus.textContent = (kind === "logo" ? "Logo" : "Imagem do QR Code") + " removido da prévia.";
        updateCustomPreview();
      });
    });
    if (qrToggle) qrToggle.addEventListener("change", function () {
      if (customStatus) customStatus.textContent = qrToggle.checked ? (custom.qr ? "QR Code aplicado à prévia." : "QR ilustrativo ativado; ele não pode ser escaneado.") : "QR Code removido da prévia.";
      updateCustomPreview();
    });
    sizeButtons.forEach(function (button) {
      button.addEventListener("click", function () { size = button.getAttribute("data-plate-size"); showVariant(); });
    });
    colorButtons.forEach(function (button) {
      button.addEventListener("click", function () { color = button.getAttribute("data-plate-color"); showVariant(); });
    });
    showVariant();
    updateCustomPreview();
  }

  // Traço decorativo de rolagem, oculto para tecnologias assistivas.
  var scrollIndicator = document.createElement("div");
  scrollIndicator.className = "scroll-indicator";
  scrollIndicator.setAttribute("aria-hidden", "true");
  document.body.appendChild(scrollIndicator);
  var progressQueued = false;
  function updateProgress() {
    var root = document.documentElement;
    var max = root.scrollHeight - window.innerHeight;
    var value = max > 0 ? Math.max(0, Math.min(1, window.scrollY / max)) : 0;
    scrollIndicator.style.transform = "scaleX(" + value + ")";

    progressQueued = false;
  }
  window.addEventListener("scroll", function () {
    if (!progressQueued) {
      progressQueued = true;
      window.requestAnimationFrame(updateProgress);
    }
  }, { passive: true });
  updateProgress();

  if (reduceMotion || !("IntersectionObserver" in window)) return;

  // Entradas de conteúdo em blocos, com cadência curta e pausa fora da tela.
  var revealSelector = "main section h2,main .lead,main .spec,main .studio,main .card,main .slot,main .values>div,main .facts>div,main .box,main .tap,main form,main .steps li,main .duo-col,main .hero-signals,main .three-preview,main .three-option-panel";
  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
  Array.prototype.forEach.call(document.querySelectorAll(revealSelector), function (el) {
    if (el.closest(".hero-x,.page-head,.err-summary,.review")) return;
    var siblings = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
    el.style.setProperty("--d", Math.min(siblings, 5));
    el.classList.add("rv");
    revealObserver.observe(el);
  });

  // Demonstração do NFC só roda enquanto a seção está visível.
  var tapSection = document.querySelector(".tapsec");
  if (tapSection) {
    new IntersectionObserver(function (entries) {
      tapSection.classList.toggle("play", entries[0].isIntersecting);
    }, { threshold: 0.35 }).observe(tapSection);
  }

  // Reflexo que acompanha o cursor e uma inclinação discreta da placa 3D.
  var hero = document.querySelector(".hero-x");
  var stage = document.querySelector(".product-stage");
  if (!hero || !stage || !finePointer) return;
  var state = { tx: 0, ty: 0, x: 0, y: 0, run: false, visible: true };
  function frame() {
    state.x += (state.tx - state.x) * 0.09;
    state.y += (state.ty - state.y) * 0.09;
    stage.style.setProperty("--tilt-x", state.x.toFixed(3));
    stage.style.setProperty("--tilt-y", state.y.toFixed(3));
    hero.style.setProperty("--lx", (stage.offsetLeft + stage.clientWidth * (state.x * .08 + .5)) + "px");
    hero.style.setProperty("--ly", (stage.offsetTop + stage.clientHeight * (state.y * .08 + .45)) + "px");
    var moving = Math.abs(state.tx - state.x) + Math.abs(state.ty - state.y) > .01;
    if (moving && state.visible) window.requestAnimationFrame(frame);
    else state.run = false;
  }
  function kick() {
    if (!state.run && state.visible) { state.run = true; window.requestAnimationFrame(frame); }
  }
  stage.addEventListener("pointermove", function (event) {
    var rect = stage.getBoundingClientRect();
    state.tx = Math.max(-1, Math.min(1, ((event.clientX - rect.left) / rect.width - .5) * 2));
    state.ty = Math.max(-1, Math.min(1, ((event.clientY - rect.top) / rect.height - .5) * 2));
    stage.style.setProperty("--mx", (event.clientX - rect.left) + "px");
    stage.style.setProperty("--my", (event.clientY - rect.top) + "px");
    kick();
  });
  stage.addEventListener("pointerleave", function () { state.tx = 0; state.ty = 0; kick(); });
  new IntersectionObserver(function (entries) {
    state.visible = entries[0].isIntersecting;
    if (state.visible) kick();
  }).observe(stage);

  // Luz localizada nos cartões e deslocamento sutil dos botões.
  Array.prototype.forEach.call(document.querySelectorAll(".card,.duo-col,.box"), function (el) {
    el.addEventListener("pointermove", function (event) {
      var rect = el.getBoundingClientRect();
      el.style.setProperty("--mx", (event.clientX - rect.left) + "px");
      el.style.setProperty("--my", (event.clientY - rect.top) + "px");
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".hero-actions .btn"), function (button) {
    button.addEventListener("pointermove", function (event) {
      var rect = button.getBoundingClientRect();
      var dx = ((event.clientX - rect.left) / rect.width - .5) * 4;
      var dy = ((event.clientY - rect.top) / rect.height - .5) * 3;
      button.style.translate = dx.toFixed(1) + "px " + dy.toFixed(1) + "px";
    });
    button.addEventListener("pointerleave", function () { button.style.translate = ""; });
  });
})();

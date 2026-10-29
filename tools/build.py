#!/usr/bin/env python3
"""Gera o site estático da AxoLabz (HTML/CSS/JS puros) para o GitHub Pages.
Uso: python3 tools/build.py   (opcional: OUT=pasta-de-saida)
Para trocar números, preços, fotos e links edite assets/js/config.js, não este arquivo."""
import os, shutil, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT") or os.path.dirname(HERE)
FONTS = os.environ.get("FONTS_DIR") or os.path.join(OUT, "assets", "fonts")

# ---------- logo ----------
STROKE = 'fill="none" stroke="currentColor" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"'
A_X = '<path d="M4 50 L22 8 L40 50 M11.5 35 H32.5"/><path d="M50 24 L72 50 M72 24 L50 50"/>'
FULL_LET = (A_X + '<circle cx="92" cy="37" r="13"/>'
            '<path d="M134 8 V50 H156"/><circle cx="178" cy="37" r="13"/><path d="M191 24 V50"/>'
            '<path d="M206 8 V50"/><circle cx="219" cy="37" r="13"/><path d="M242 24 H266 L242 50 H266"/>')
def gills(ds):
    return ('<g fill="none" stroke="var(--gill,#17b0bf)" stroke-width="4.6" stroke-linecap="round">' +
            ''.join(f'<path class="g" pathLength="1" d="{d}"/>' for d in ds) + '</g>')
G_FULL = gills(["M100 28 C106 22 109 16 108 8", "M104 34 C111 31 116 26 118 19", "M105 40 C112 40 118 37 122 32"])
G_MARK = gills(["M75 24 C81 19 84 14 83 7", "M77 31 C84 29 88 25 90 19", "M77 38 C83 38 88 36 91 32"])

def logo_svg(mark=False, cls=""):
    vb = "0 0 94 60" if mark else "0 0 272 60"
    body = f'<g {STROKE}>{A_X if mark else FULL_LET}</g>' + (G_MARK if mark else G_FULL)
    return f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true" focusable="false">{body}</svg>'

def wordmark_svg():
    head, rest = logo_svg(False, "full").split('</g>', 1)
    k = [0]
    def rep(m):
        k[0] += 1
        return f'{m.group(1)} pathLength="1" style="--k:{k[0]}"'
    return re.sub(r'(<(?:path|circle))(?= )', rep, head) + '</g>' + rest

def logo_file(mark=False, color="#1e2429", gill="#17b0bf"):
    vb = "0 0 94 60" if mark else "0 0 272 60"
    body = f'<g {STROKE}>{A_X if mark else FULL_LET}</g>' + (G_MARK if mark else G_FULL)
    body = body.replace('class="g" pathLength="1" ', '').replace("var(--gill,#17b0bf)", gill)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="AxoLabz" style="color:{color}">{body}</svg>'

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1e2429"/>'
           '<g transform="translate(7 17) scale(.52)" style="color:#fff">' +
           f'<g {STROKE}>{A_X}</g>' + G_MARK.replace('class="g" pathLength="1" ', '').replace("var(--gill,#17b0bf)", "#5cd6e3") + '</g></svg>')

# ---------- ilustrações ----------
def qr_placeholder(x, y, size):
    """A decorative, deliberately non-scannable QR stand-in for the live preview."""
    module = size / 15
    blocks = []
    for row in range(15):
        for col in range(15):
            finder = None
            for fx, fy in ((0, 0), (10, 0), (0, 10)):
                if fx <= col < fx + 5 and fy <= row < fy + 5:
                    finder = (col - fx, row - fy)
                    break
            if finder is not None:
                dx, dy = finder
                on = dx in (0, 4) or dy in (0, 4) or (dx == 2 and dy == 2)
            else:
                on = (row * 7 + col * 11 + row * col * 3) % 5 in (0, 1)
            if on:
                blocks.append(f'<rect x="{x + col * module:.2f}" y="{y + row * module:.2f}" width="{module:.2f}" height="{module:.2f}"/>')
    return (f'<g data-plate-qr-placeholder><rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" rx="{size*.08:.1f}" fill="#fff"/>'
            f'<g fill="#20262b">{"".join(blocks)}</g></g>')

def plate(size, color):
    # As duas versões seguem a proporção física 64 x 100 mm e 80 x 125 mm.
    w, h = (128, 200) if size == "M" else (160, 250)
    s = w / 128
    x, y = (260 - w) / 2, 272 - h
    dark = color == "preta"
    fill, stroke = ("#20262b", "#0f1316") if dark else ("#f7f9fa", "#c3ccd3")
    fg = "#ffffff" if dark else "#1e2429"
    cx = 130
    logo_w, logo_h = w * .72, h * .27
    logo_x, logo_y = cx - logo_w / 2, y + h * .075
    logo_label_y = logo_y + logo_h * .59
    qr_size, qr_x, qr_y = w * .36, x + w * .08, y + h * .61
    nfc_cy = qr_y + qr_size / 2
    nfc_r = qr_size * .51
    def nfc_icon(center_x, position, hidden=False):
        ox = center_x - 8 * s
        arcs = "".join(f'<path d="M{ox + r*.7:.1f} {nfc_cy - r*.7:.1f} A{r:.1f} {r:.1f} 0 0 1 {ox + r*.7:.1f} {nfc_cy + r*.7:.1f}"/>' for r in (6 * s, 11 * s, 16 * s))
        style = ' style="display:none"' if hidden else ""
        return (f'<g data-plate-nfc-{position}{style}><circle cx="{center_x:.1f}" cy="{nfc_cy:.1f}" r="{nfc_r:.1f}" fill="none" stroke="{fg}" stroke-width="{2.2*s:.1f}"/>'
                f'<g fill="none" stroke="{fg}" stroke-width="{2.2*s:.1f}" stroke-linecap="round">{arcs}</g></g>')
    return (f'<svg class="plate" viewBox="0 0 260 300" role="img" aria-label="Ilustração da placa {size} {color}">'
            f'<ellipse cx="130" cy="282" rx="{w*.55:.0f}" ry="6" fill="#000" opacity=".12"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="{14*s:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<g data-plate-default-copy><rect x="{logo_x:.1f}" y="{logo_y:.1f}" width="{logo_w:.1f}" height="{logo_h:.1f}" rx="{5*s:.1f}" fill="none" stroke="{fg}" stroke-opacity=".28" stroke-width="{1.2*s:.1f}" stroke-dasharray="{3*s:.1f} {3*s:.1f}"/>'
            f'<text x="{cx}" y="{logo_label_y:.1f}" text-anchor="middle" font-size="{9*s:.1f}" font-weight="700" letter-spacing="{1.1*s:.1f}" fill="{fg}" opacity=".72">SUA LOGO</text></g>'
            f'<image data-plate-logo x="{logo_x:.1f}" y="{logo_y:.1f}" width="{logo_w:.1f}" height="{logo_h:.1f}" preserveAspectRatio="xMidYMid meet" style="display:none"/>'
            f'{qr_placeholder(qr_x, qr_y, qr_size)}'
            f'<rect data-plate-qr-bg x="{qr_x:.1f}" y="{qr_y:.1f}" width="{qr_size:.1f}" height="{qr_size:.1f}" rx="{qr_size*.08:.1f}" fill="#fff" style="display:none"/>'
            f'<image data-plate-qr x="{qr_x:.1f}" y="{qr_y:.1f}" width="{qr_size:.1f}" height="{qr_size:.1f}" preserveAspectRatio="xMidYMid meet" style="display:none"/>'
            f'{nfc_icon(x + w * .76, "right")}{nfc_icon(cx, "center", hidden=True)}</svg>')

BROWSER = ('<svg viewBox="0 0 320 220" role="img" aria-label="Ilustração de um site aberto no navegador">'
           '<rect x="2" y="2" width="316" height="216" rx="12" fill="#fff" stroke="#c3ccd3" stroke-width="2"/>'
           '<path d="M2 34 H318" stroke="#d9dfe5" stroke-width="2"/>'
           '<circle cx="20" cy="18" r="4" fill="#c3ccd3"/><circle cx="34" cy="18" r="4" fill="#c3ccd3"/><circle cx="48" cy="18" r="4" fill="#c3ccd3"/>'
           '<rect x="80" y="10" width="160" height="16" rx="8" fill="#f2f5f7"/>'
           '<rect x="16" y="48" width="288" height="78" rx="8" fill="#e8f1ff"/>'
           '<rect x="30" y="62" width="130" height="10" rx="5" fill="#1e2429"/>'
           '<rect x="30" y="80" width="170" height="6" rx="3" fill="#78848f"/><rect x="30" y="92" width="120" height="6" rx="3" fill="#78848f"/>'
           '<rect x="30" y="106" width="64" height="14" rx="7" fill="#1c5fd0"/>'
           '<rect x="210" y="60" width="82" height="56" rx="8" fill="#17b0bf" opacity=".35"/>'
           '<rect x="16" y="138" width="90" height="66" rx="8" fill="#f2f5f7"/><rect x="115" y="138" width="90" height="66" rx="8" fill="#f2f5f7"/><rect x="214" y="138" width="90" height="66" rx="8" fill="#f2f5f7"/></svg>')

def thumb(inner):
    return f'<svg viewBox="0 0 200 110" aria-hidden="true" focusable="false">{inner}</svg>'
def rect(x, y, w, h, f, r=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{f}"/>'
GRAY, BLUE, INK, MUTE, CYAN = "#d9dfe5", "#1c5fd0", "#1e2429", "#78848f", "#17b0bf"
GEAR = "".join(f'<rect x="96" y="22" width="8" height="12" rx="2" fill="{BLUE}" transform="rotate({a} 100 55)"/>' for a in range(0, 360, 45))
THUMBS = {
    "landing-page": thumb(rect(10, 8, 180, 62, "#e8f1ff", 8) + rect(24, 20, 80, 9, INK, 4) + rect(24, 36, 110, 5, MUTE, 2.5) + rect(24, 48, 50, 12, BLUE) + rect(10, 80, 86, 22, GRAY) + rect(104, 80, 86, 22, GRAY)),
    "site-institucional": thumb(rect(10, 8, 180, 14, GRAY, 5) + rect(10, 30, 56, 72, "#e8f1ff") + rect(72, 30, 56, 72, "#e8f1ff") + rect(134, 30, 56, 72, "#e8f1ff") + rect(18, 40, 30, 6, INK, 3) + rect(80, 40, 30, 6, INK, 3) + rect(142, 40, 30, 6, INK, 3)),
    "catalogo-whatsapp": thumb("".join(rect(10 + i * 62, 10 + j * 46, 56, 40, GRAY if (i + j) % 2 else "#e8f1ff") for i in range(3) for j in range(2)) + f'<circle cx="172" cy="84" r="14" fill="{CYAN}"/>' + rect(166, 80, 12, 3, "#fff", 1.5) + rect(166, 86, 8, 3, "#fff", 1.5)),
    "loja-virtual": thumb(rect(10, 10, 56, 60, "#e8f1ff") + rect(72, 10, 56, 60, GRAY) + rect(134, 10, 56, 60, "#e8f1ff") + rect(10, 78, 40, 8, INK, 4) + rect(72, 78, 40, 8, INK, 4) + rect(134, 78, 40, 8, INK, 4) + rect(10, 92, 24, 10, BLUE, 5) + rect(72, 92, 24, 10, BLUE, 5) + rect(134, 92, 24, 10, BLUE, 5)),
    "manutencao": thumb(GEAR + f'<circle cx="100" cy="55" r="21" fill="none" stroke="{BLUE}" stroke-width="9"/><circle cx="100" cy="55" r="7" fill="{CYAN}"/>'),
}
GILL_ART = ('<svg class="gill-art" viewBox="0 0 400 400" aria-hidden="true" focusable="false">'
            + "".join(f'<path pathLength="1" d="{d}"/>' for d in [
                "M395 390 C340 310 330 190 255 95", "M338 262 C305 262 282 244 270 214",
                "M327 205 C350 188 358 158 350 126", "M296 150 C270 150 252 138 242 118", "M395 330 C360 300 350 260 352 236"]) + '</svg>')

# ---------- conteúdo ----------
SERVICES = {
    "landing-page": dict(
        name="Landing page",
        short="Uma página para apresentar seu negócio ou levar o visitante a uma ação, como pedir um orçamento.",
        goal="Apresentar seu negócio ou conduzir o visitante a uma ação específica, como chamar no WhatsApp, em uma única página. O foco (conversão ou apresentação) é definido conforme a sua necessidade.",
        deliver=["Página única, adaptada para celular, tablet e computador", "Textos e imagens organizados a partir do material combinado", "Botões de contato conforme a proposta", "Arquivos finais e instruções de entrega, conforme o serviço contratado"],
        included=["As funcionalidades descritas na proposta aprovada de cada projeto", "Uma rodada consolidada de revisão, conforme o escopo contratado"],
        limits=["Uma página. Mais páginas pedem outro serviço ou um orçamento específico", "Criação de textos, fotos e identidade visual depende do que for combinado na proposta", "Funcionalidades que não estão na proposta não estão incluídas"],
        extras=["Revisões além da rodada incluída", "Novas funcionalidades e mudanças fora do escopo aprovado", "Domínio e hospedagem: ficam em nome do cliente e são pagos por ele (a AxoLabz pode orientar a configuração)"],
        price="digital:landing-page"),
    "site-institucional": dict(
        name="Site institucional",
        short="Pacote inicial de até cinco páginas para apresentar sua empresa com mais profundidade.",
        goal="Apresentar a empresa, os serviços e as formas de contato em um site organizado, com cada assunto em sua própria página.",
        deliver=["Pacote inicial de até cinco páginas", "Navegação entre as páginas e layout adaptado a celular, tablet e computador", "Arquivos finais e instruções de entrega, conforme o serviço contratado"],
        included=["As funcionalidades descritas na proposta aprovada", "Uma rodada consolidada de revisão, conforme o escopo contratado"],
        limits=["Até cinco páginas no pacote inicial. Páginas adicionais são avaliadas e orçadas separadamente", "Conteúdo, funcionalidades, prazos e valor final dependem do escopo aprovado"],
        extras=["Páginas adicionais", "Revisões além da rodada incluída", "Novas funcionalidades e mudanças fora do escopo aprovado", "Domínio e hospedagem: ficam em nome do cliente e são pagos por ele (a AxoLabz pode orientar a configuração)"],
        price="digital:site-institucional"),
    "catalogo-whatsapp": dict(
        name="Catálogo digital com WhatsApp",
        short="Seus produtos ou serviços organizados, com pedidos e consultas encaminhados ao WhatsApp.",
        goal="Apresentar produtos ou serviços com as informações bem organizadas e permitir que o cliente envie um pedido ou uma consulta pelo WhatsApp.",
        deliver=["Catálogo com itens e informações organizados", "Botões que levam o cliente ao WhatsApp com a mensagem preparada", "Arquivos finais e instruções de entrega, conforme o serviço contratado"],
        included=["As funcionalidades específicas definidas no orçamento", "Uma rodada consolidada de revisão, conforme o escopo contratado"],
        limits=["As funcionalidades específicas são definidas no orçamento, não antes", "Pagamento online e gestão de pedidos não fazem parte deste serviço; para isso, consulte a loja virtual"],
        extras=["Itens além da quantidade definida na proposta", "Revisões além da rodada incluída", "Novas funcionalidades e mudanças fora do escopo aprovado", "Domínio e hospedagem: ficam em nome do cliente e são pagos por ele"],
        price="digital:catalogo-whatsapp"),
    "loja-virtual": dict(
        name="Loja virtual (e-commerce)",
        short="Venda online sob consulta. Cada pedido passa por uma avaliação individual.",
        goal="Vender online com produtos, pedidos e pagamentos. Como cada loja tem necessidades diferentes, o serviço é feito sob consulta, depois de uma avaliação individual.",
        deliver=["Definidos depois da avaliação individual do seu caso"],
        included=["Nenhuma funcionalidade é prometida antes da avaliação", "Pagamentos, produtos, pedidos e necessidades de gestão são analisados caso a caso"],
        limits=["Funcionalidades de e-commerce só entram na proposta depois de avaliadas", "Escopo, prazo e valor são definidos na proposta, por escrito"],
        extras=["Tudo o que ficar fora do escopo aprovado, avaliado e orçado separadamente", "Domínio e hospedagem: ficam em nome do cliente e são pagos por ele"],
        price=None),
    "manutencao": dict(
        name="Manutenção opcional",
        short="Acompanhamento depois da entrega. É um serviço adicional, nunca obrigatório.",
        goal="Acompanhar o site depois da entrega, com ajustes e atualizações combinados. É um serviço adicional e opcional.",
        deliver=["Escopo definido na proposta"],
        included=["Os itens e a frequência combinados na proposta"],
        limits=["Serviço opcional: contratar o site não obriga a contratar a manutenção", "Não há suporte ilimitado: o que está coberto fica descrito na proposta"],
        extras=["O que ficar fora do escopo combinado, avaliado e orçado separadamente"],
        price="digital:manutencao", pending="Preço definido na proposta"),
}
STEPS = [("Entendemos a necessidade", "Ouvimos o que o seu negócio precisa e qual resultado você espera."),
         ("Planejamos a solução", "Definimos o caminho mais simples para chegar lá."),
         ("Definimos e aprovamos o escopo", "Você recebe a proposta por escrito e aprova antes de começarmos."),
         ("Executamos o trabalho", "Produzimos o site ou a placa conforme o combinado."),
         ("Testamos e verificamos a qualidade", "Conferimos o funcionamento e os detalhes antes de entregar."),
         ("Entregamos o resultado", "Você recebe o trabalho e as instruções necessárias.")]
VARIANTS = [("M", "branca", "Branca"), ("M", "preta", "Preta"), ("G", "branca", "Branca"), ("G", "preta", "Preta")]

def steps_html(longer=False):
    return '<ol class="steps">' + "".join(f'<li style="--i:{i}"><strong>{t}</strong><p>{d}</p></li>' for i, (t, d) in enumerate(STEPS)) + '</ol>'
def lis(items): return "".join(f"<li>{i}</li>" for i in items)

# ---------- estrutura comum ----------
NAV = [("index.html", "Início", "inicio"), ("digital.html", "Digital", "digital"), ("3d.html", "3D", "3d"), ("sobre.html", "Sobre", "sobre"), ("contato.html", "Contato", "contato")]
WA_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.7 7.1L4 20l1-4.8A8 8 0 1 1 21 12z"/></svg>'
PAGES = {}

def page(path, title, desc, body, cur=None, exact=True, forms=False, float_=True, home=False, page_css=None):
    r = "../" * path.count("/")
    nav = ""
    for href, label, key in NAV:
        attr = ""
        if key == cur:
            attr = ' aria-current="page"' if exact else ' aria-current="true"'
        nav += f'<li><a href="{r}{href}"{attr}>{label}</a></li>'
    fl = f'<a class="wa-float" data-wa href="{r}contato.html#aviso-whatsapp">{WA_ICON}WhatsApp</a>' if float_ else ""
    foot_nav = "".join(f'<li><a href="{r}{h}">{l}</a></li>' for h, l, _ in NAV)
    PAGES[path] = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#10171b">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/archivo-latin-wdth-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/css/style.css">
{f'<link rel="stylesheet" href="{r}{page_css}">' if page_css else ""}
<script>document.documentElement.classList.add("js");if(!matchMedia("(prefers-reduced-motion:reduce)").matches)document.documentElement.classList.add("anim")</script>
<script src="{r}assets/js/config.js" defer></script>
<script src="{r}assets/js/app.js" defer></script>
<script src="{r}assets/js/motion.js" defer></script>{'<script src="' + r + 'assets/js/forms.js" defer></script>' if forms else ''}
</head>
<body data-root="{r}" class="{'has-float' if float_ else ''}{' home' if home else ''}">
<a class="skip" href="#conteudo">Ir para o conteúdo</a>
<header class="site-head{' over' if home else ''}" id="topo"><div class="wrap head-in">
<a class="logo" href="{r}index.html" aria-label="AxoLabz, página inicial">{logo_svg(False, "full")}{logo_svg(True, "mark")}</a>
<button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="nav" id="site-nav" aria-label="Principal"><ul>{nav}</ul></nav>
</div></header>
<main id="conteudo">
{body}
</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div><a class="logo" href="{r}index.html" aria-label="AxoLabz, página inicial">{logo_svg(False, "full")}</a><p style="margin-top:1rem">Tecnologia que transforma ideias em soluções.</p><p data-city data-prefix="Cidade: "></p></div>
<div><h2>Navegação</h2><ul>{foot_nav}</ul></div>
<div><h2>Contato</h2><ul><li data-wa-item><a data-wa href="{r}contato.html#aviso-whatsapp">WhatsApp</a></li><li data-ig-item><a data-ig href="{r}contato.html" rel="noopener">Instagram</a></li><li><a href="{r}contato.html">Pedir orçamento</a></li></ul></div>
<div><h2>Informações</h2><ul><li><a href="{r}privacidade.html">Aviso de privacidade</a></li><li><a href="{r}condicoes.html">Condições comerciais</a></li></ul></div>
</div>
<p class="legal">© <span data-year>2026</span> AxoLabz. Todos os direitos reservados.</p>
</div></footer>
{fl}
</body>
</html>
'''

def head(title, lead, crumbs=None):
    c = ""
    if crumbs:
        c = '<nav class="crumb" aria-label="Você está em">' + " &rsaquo; ".join(f'<a href="{h}">{t}</a>' for h, t in crumbs) + "</nav>"
    return f'<div class="page-head"><div class="wrap">{c}<h1>{title}</h1><p class="lead">{lead}</p></div></div>'

def art(inner, caption="Imagem ilustrativa", photo=None, alt="Placa AxoLabz"):
    ph = f' data-photo="{photo}" data-alt="{alt}"' if photo else ""
    return f'<figure class="art" style="margin:0"><div{ph}>{inner}</div><figcaption data-illus>{caption}</figcaption></figure>'

NO_WA = ('<div class="notice warn" id="aviso-whatsapp" data-if-no-wa hidden><p><strong>O WhatsApp da AxoLabz ainda não está disponível neste site.</strong> '
         'Você pode preparar sua mensagem pelos formulários e copiá-la para enviar depois.</p></div>')

# ---------- formulários ----------
def f_input(name, label, req=False, hint="", typ="text", extra=""):
    rq = ' <span class="req">(obrigatório)</span>' if req else ""
    desc = (f"h-{name} " if hint else "") + f"err-{name}"
    h = f'<p class="hint" id="h-{name}">{hint}</p>' if hint else ""
    ar = ' aria-required="true"' if req else ""
    return (f'<div class="field"><label for="{name}">{label}{rq}</label>{h}'
            f'<input type="{typ}" id="{name}" name="{name}" aria-describedby="{desc}"{ar} {extra}>'
            f'<p class="err" id="err-{name}"></p></div>')

def f_area(name, label, hint=""):
    h = f'<p class="hint" id="h-{name}">{hint}</p>' if hint else ""
    return (f'<div class="field"><label for="{name}">{label}</label>{h}'
            f'<textarea id="{name}" name="{name}" maxlength="600" aria-describedby="{"h-"+name if hint else ""}"></textarea></div>')

def f_check(name, id_, value, label, hint=""):
    return (f'<div class="opt"><input type="checkbox" id="{id_}" name="{name}" value="{value}" data-label="{value}">'
            f'<label for="{id_}">{label}</label></div>')

DIGITAL_FORM = f'''<form data-form="digital" novalidate aria-label="Pedido de orçamento">
<div class="err-summary" role="alert" tabindex="-1" hidden></div>
<fieldset aria-describedby="err-tipo"><legend>Tipo de projeto</legend>
''' + "".join(
    f'<div class="opt"><input type="radio" id="tipo-{i}" name="tipo" value="{v}" data-label="{l}"><label for="tipo-{i}">{l}</label></div>'
    for i, (v, l) in enumerate([("landing-page", "Landing page"), ("site-institucional", "Site institucional"), ("catalogo-whatsapp", "Catálogo digital com WhatsApp"), ("loja-virtual", "Loja virtual (sob consulta)")], 1)
) + '''<p class="err" id="err-tipo"></p>
<div class="opt"><input type="checkbox" id="orientacao" name="orientacao"><label for="orientacao">Ainda não sei qual solução escolher e preciso de orientação</label></div>
</fieldset>
''' + f_input("negocio", "Nome do negócio", True) + f_input("paginas", "Quantidade de páginas desejada", False, "Se aplicável. O pacote inicial do site institucional tem até cinco páginas; páginas adicionais são orçadas separadamente.", "number", 'min="1" max="50" inputmode="numeric"') + '''
<fieldset><legend>Funcionalidades desejadas</legend>
''' + "".join(f_check("func", f"func-{i}", t, t) for i, t in enumerate([
    "Botão de WhatsApp", "Links para Instagram e outras redes sociais", "Galeria de fotos", "Catálogo de produtos ou serviços",
    "Mapa ou localização", "Formulário de contato", "Seção de perguntas frequentes", "Ainda não sei; preciso de orientação"], 1)) + '''
</fieldset>
''' + f_area("obs", "Observações", "Conte o que for útil: prazo desejado, referências, dúvidas.") + '''
<button class="btn" type="submit">Revisar solicitação</button>
</form>
<div class="review" hidden tabindex="-1"></div>'''

def pedido_form():
    v = "".join(
        f'<label class="vopt" for="variante-{i}"><input type="radio" id="variante-{i}" name="variante" value="{s}-{c}" data-size="{s}" data-color="{n}">'
        f'<span><span class="sw {"p" if c=="preta" else "b"}"></span>{s} {c}</span><small>Tamanho {s}, cor {n.lower()}</small></label>'
        for i, (s, c, n) in enumerate(VARIANTS, 1))
    return f'''<form data-form="pedido" novalidate aria-label="Pedido de placa">
<div class="err-summary" role="alert" tabindex="-1" hidden></div>
<fieldset aria-describedby="err-variante"><legend>Variante da placa</legend><div class="variants">{v}</div><p class="err" id="err-variante"></p></fieldset>
{f_input("estab", "Nome do estabelecimento", True)}
{f_input("link", "Link de avaliação do Google", True, "Cole o link que leva direto à janela de avaliação do seu negócio.", "text", 'inputmode="url" autocomplete="off"')}
<details class="how"><summary>Como copiar o link correto</summary>
<ol><li>Com o acesso ao Perfil da Empresa no Google, pesquise o nome do seu negócio no Google.</li><li>Toque ou clique em “Pedir avaliações”.</li><li>Copie o link exibido e cole no campo acima.</li></ol>
<p>Não achou? Fale com a AxoLabz pela <a href="../contato.html">página de contato</a> e peça ajuda para localizar o link.</p></details>
<div class="field"><div class="opt"><input type="checkbox" id="qr" name="qr" value="sim" checked><label for="qr">Quero o QR Code adicional (opcional)</label></div>
<p class="hint">O NFC já está incluso. QR Code adicional: <span id="qr-price">Valor a confirmar</span>.</p><p class="hint">Se personalizou a prévia, envie os arquivos no WhatsApp depois de revisar o pedido.</p></div>
{f_area("obs", "Observações (opcional)")}
<button class="btn" type="submit">Revisar solicitação</button>
</form>
<div class="review" hidden tabindex="-1"></div>'''

def nfc_demo():
    return f'''<section class="tapsec" id="como-funciona" aria-labelledby="tap-title"><div class="wrap split">
<div><p class="hero-kicker tap-kicker"><i aria-hidden="true"></i> NFC EM AÇÃO</p><h2 id="tap-title">Aproxime. Leia. Avalie.</h2>
<ol class="tap-steps"><li><strong>Aproxime</strong> o celular da placa.</li><li><strong>O NFC</strong>, que já vem incluso, leva o celular ao seu link de avaliação.</li><li><strong>O cliente avalia</strong> o seu negócio no Google.</li></ol>
<p class="fine">Demonstração ilustrativa. O QR Code é um adicional opcional da placa.</p></div>
<div class="tap" aria-hidden="true"><div class="tap-plate">{plate("G", "preta")}<i class="rip"></i><i class="rip"></i><i class="rip"></i></div>
<div class="tap-phone"><div class="scr"><b></b><span class="stars"><u style="--i:0"></u><u style="--i:1"></u><u style="--i:2"></u><u style="--i:3"></u><u style="--i:4"></u></span><em></em></div></div></div>
</div></section>'''
# ---------- páginas ----------
def build_pages():
    # Início
    page("index.html", "AxoLabz | Tecnologia que transforma ideias em soluções",
         "AxoLabz Digital e AxoLabz 3D: sites, catálogos com WhatsApp e placas de avaliação do Google feitas sob encomenda.",
         f'''<section class="hero-x" aria-labelledby="hero-title"><div class="wrap hero-layout">
<div class="hero-copy">
<div class="wordmark hero-wordmark">{wordmark_svg()}</div>
<p class="hero-kicker"><i aria-hidden="true"></i> DIGITAL <span>·</span> 3D</p>
<h1 id="hero-title"><span class="hero-title-line">Tecnologia que</span><em class="hero-title-line">transforma ideias</em><span class="hero-title-line">em soluções.</span></h1>
<p class="hero-deck">Sites e catálogos para pequenos negócios. Placas de avaliação em 3D feitas para o balcão do seu negócio.</p>
<div class="hero-actions"><a class="btn" href="digital.html">Conhecer AxoLabz Digital <span aria-hidden="true">↗</span></a><a class="btn line" href="3d.html">Explorar AxoLabz 3D <span aria-hidden="true">↗</span></a></div>
<div class="hero-signals"><span><i aria-hidden="true">✓</i> Escopo por escrito</span><span><i aria-hidden="true">↗</i> Feito sob encomenda</span></div>
</div>
<div class="hero-product" data-product-viewer>
<div class="product-stage">
<div class="product-grid" aria-hidden="true"></div><div class="product-orbit orbit-one" aria-hidden="true"></div><div class="product-orbit orbit-two" aria-hidden="true"></div>
<div class="plate-options">
<figure class="plate-option" data-plate-option="M-branca" hidden><div data-photo="M-branca" data-alt="Placa M branca">{plate("M", "branca")}</div></figure>
<figure class="plate-option" data-plate-option="M-preta" hidden><div data-photo="M-preta" data-alt="Placa M preta">{plate("M", "preta")}</div></figure>
<figure class="plate-option" data-plate-option="G-branca" hidden><div data-photo="G-branca" data-alt="Placa G branca">{plate("G", "branca")}</div></figure>
<figure class="plate-option is-active" data-plate-option="G-preta"><div data-photo="G-preta" data-alt="Placa G preta">{plate("G", "preta")}</div></figure>
</div>
<div class="product-chip chip-new"><span aria-hidden="true">✦</span> NOVIDADE</div>
<div class="product-chip chip-nfc"><span class="nfc-glyph" aria-hidden="true">)))</span> NFC INCLUSO</div>
<div class="product-chip chip-variant"><span data-selected-size>G</span> <i>·</i> <span data-selected-color>Preta</span></div>
<span class="visually-hidden" data-variant-status aria-live="polite">Placa G preta selecionada</span>
</div>
<div class="variant-controls" role="group" aria-label="Simule sua placa"><p class="variant-heading">Simule sua placa</p>
<div class="control-set" role="group" aria-label="Escolha o tamanho"><span>Tamanho</span><button type="button" data-plate-size="M" aria-pressed="false">M</button><button type="button" data-plate-size="G" aria-pressed="true">G</button></div>
<div class="control-set color-set" role="group" aria-label="Escolha a cor"><span>Cor</span><button type="button" class="color-choice" data-plate-color="branca" aria-label="Branca" aria-pressed="false"><i class="swatch swatch-light"></i>Branca</button><button type="button" class="color-choice" data-plate-color="preta" aria-label="Preta" aria-pressed="true"><i class="swatch swatch-dark"></i>Preta</button></div>
</div><a class="variant-order" data-order-variant href="produtos/placa-avaliacao-google.html?v=G-preta">Pedir esta placa <span aria-hidden="true">↗</span></a>
</div>
<a class="hero-scroll" href="#solucoes"><span></span>Role para explorar</a>
</div></section>
<section class="duo" id="solucoes"><div class="wrap duo-grid">
<article class="duo-col"><div class="duo-head"><h2>AxoLabz Digital</h2>
<dl class="spec"><dt>Para</dt><dd>Pequenos negócios e empresas locais</dd><dt>Serviços</dt><dd>5, de landing page a loja virtual</dd><dt>Orçamento</dt><dd>Por escrito</dd><dt>A partir de</dt><dd data-price="digital:landing-page">Valor a confirmar</dd></dl></div>
<div class="studio">{BROWSER}</div>
<p class="fine">Exemplo ilustrativo de site. O valor é uma referência: o orçamento final depende do escopo.</p>
<div class="actions"><a class="btn" href="digital.html">Conhecer os serviços</a></div></article>
<article class="duo-col"><div class="duo-head"><h2>AxoLabz 3D</h2>
<dl class="spec"><dt>Produto</dt><dd>Placa de avaliação do Google</dd><dt>Tamanho M</dt><dd>64 × 100 × 4 mm · 80%</dd><dt>Tamanho G</dt><dd>80 × 125 × 5 mm · 100%</dd><dt>Cores</dt><dd>Branca e preta</dd><dt>NFC</dt><dd>Incluso</dd><dt>QR Code</dt><dd>Opcional</dd><dt>Preço M</dt><dd data-price="plate:M">Preço sob consulta</dd><dt>Preço G</dt><dd data-price="plate:G">Preço sob consulta</dd></dl></div>
<div class="studio"><div data-photo="G-branca" data-alt="Placa G branca">{plate("G", "branca")}</div><p class="fine" data-illus style="margin:0">Imagem ilustrativa da placa G branca</p></div>
<p class="fine">Fabricação sob encomenda. O prazo é confirmado pelo WhatsApp.</p>
<div class="actions"><a class="btn" href="3d.html">Ver o catálogo</a></div></article>
</div></section>
{nfc_demo()}
<section class="alt"><div class="wrap"><h2>Como trabalhamos</h2><p class="lead" style="margin-bottom:2rem">Seis etapas, do primeiro contato à entrega.</p>{steps_html()}</div></section>
<section class="cta-band"><div class="wrap"><h2>Vamos conversar sobre o seu projeto?</h2>
<p>Conte o que você precisa pelo WhatsApp. O orçamento dos serviços digitais é enviado por escrito.</p>
<a class="btn" data-wa href="contato.html#aviso-whatsapp">Falar no WhatsApp</a>
<div style="max-width:560px;margin:1rem 0 0" data-if-no-wa hidden><p style="color:#fff">O WhatsApp ainda não está disponível neste site. Use a <a href="contato.html" style="color:#5cd6e3">página de contato</a> para preparar sua mensagem.</p></div>
</div></section>''', cur="inicio", home=True)

    # Digital
    cards = ""
    for k, s in SERVICES.items():
        if s["price"]:
            pr = f'<span class="price" data-price="{s["price"]}" data-pending="{s.get("pending", "Valor a confirmar")}">Valor a confirmar</span>'
        else:
            pr = '<span class="price">Sob consulta</span>'
        cards += f'<a class="card" href="servicos/{k}.html"><div class="thumb">{THUMBS[k]}</div><div class="body"><h3>{s["name"]}</h3><p>{s["short"]}</p>{pr}</div></a>'
    page("digital.html", "AxoLabz Digital | Sites, catálogos e lojas virtuais",
         "Landing page, site institucional, catálogo digital com WhatsApp, loja virtual sob consulta e manutenção opcional.",
         head("AxoLabz Digital", "Presença online sob medida para pequenos negócios, comerciantes, profissionais autônomos e empresas locais.") +
         f'''<section><div class="wrap"><h2>Serviços</h2><div class="cards five">{cards}</div>
<div class="notice"><p>Os valores “a partir de” são só uma referência. O orçamento final depende do escopo do projeto e é enviado por escrito antes do início.</p></div></div></section>
<section class="alt"><div class="wrap"><h2>Projetos reais</h2><p>Os primeiros projetos aparecerão aqui quando forem concluídos e autorizados para divulgação.</p>
<div class="cards">{"".join('<div class="slot"><p>Espaço reservado para um projeto real</p></div>' for _ in range(3))}</div></div></section>
<section class="cta-band"><div class="wrap"><h2>Pronto para pedir um orçamento?</h2><p>Descreva seu projeto e prepare a mensagem para o WhatsApp.</p><a class="btn" href="contato.html#orcamento">Pedir orçamento</a></div></section>''',
         cur="digital")

    # Detalhes de serviço
    for k, s in SERVICES.items():
        price = (f'<p class="price" style="margin:0"><span data-price="{s["price"]}" data-pending="{s.get("pending", "Valor a confirmar")}">Valor a confirmar</span></p>'
                 if s["price"] else '<p class="price" style="margin:0">Sob consulta</p>')
        page(f"servicos/{k}.html", f"{s['name']} | AxoLabz Digital", s["short"],
             head(s["name"], s["short"], [("../index.html", "Início"), ("../digital.html", "Digital")]) +
             f'''<section><div class="wrap split top"><div><h2>Objetivo</h2><p>{s["goal"]}</p>
<div class="box"><p class="muted" style="margin-bottom:.3rem">Valor de referência</p>{price}
<p class="hint">É uma referência. O valor final depende do escopo aprovado na proposta.</p></div>
<div class="actions"><a class="btn" href="../contato.html?tipo={k if k != "manutencao" else "manutencao"}#orcamento">{"Pedir orçamento" if k != "manutencao" else "Perguntar sobre manutenção"}</a></div></div>
<div>{art(THUMBS[k].replace('viewBox="0 0 200 110"', 'viewBox="0 0 200 110" style="height:200px"'), "Ilustração do serviço")}</div></div></section>
<section class="alt"><div class="wrap facts">
<div><h2>Entregáveis</h2><ul class="tick">{lis(s["deliver"])}</ul></div>
<div><h2>O que está incluído</h2><ul class="tick">{lis(s["included"])}</ul></div>
<div><h2>Limites de escopo</h2><ul>{lis(s["limits"])}</ul></div>
<div><h2>Possíveis cobranças adicionais</h2><ul>{lis(s["extras"])}</ul></div>
</div></section>''', cur="digital", exact=False)

# 3D — simulador ligado diretamente às opções de tamanho e cor.
    preview_arts = ""
    for s, c, n in VARIANTS:
        active = (s, c) == ("G", "preta")
        cls = " is-active" if active else ""
        hidden = "" if active else " hidden"
        preview_arts += f'<figure class="three-preview-variant{cls}" data-plate-option="{s}-{c}"{hidden}><div data-photo="{s}-{c}" data-alt="Placa {s} {c}">{plate(s, c)}</div></figure>'
    page("3d.html", "AxoLabz 3D | Placas de avaliação com NFC",
         "Configure uma placa de avaliação do Google impressa em 3D. Compare tamanhos, cores e peça a sua com NFC incluso.",
         f'''<section class="three-intro" aria-labelledby="three-title"><div class="wrap">
<p class="three-eyebrow"><span aria-hidden="true"></span> AXOLABZ 3D <i>·</i> FEITA SOB ENCOMENDA</p>
<h1 id="three-title">Uma avaliação começa com <em>um toque.</em></h1>
<p>Escolha o tamanho e a cor, envie a logo do seu negócio e veja a prévia. O QR Code é opcional; o NFC já vem incluso.</p>
<a class="btn" href="#simulador">Personalizar minha placa <span aria-hidden="true">↓</span></a>
</div></section>
<section class="three-config-section" id="simulador" aria-labelledby="simulator-title"><div class="wrap">
<div class="three-config-heading"><div><p class="three-kicker">PRÉVIA INTERATIVA</p><h2 id="simulator-title">Monte sua placa</h2></div><p>Altere as opções e veja a prévia mudar na hora.</p></div>
<div class="three-configurator" data-product-viewer>
<figure class="three-preview" aria-label="Prévia da placa selecionada"><span class="three-preview-grid" aria-hidden="true"></span><span class="three-preview-orbit" aria-hidden="true"></span>
<div class="three-preview-options">{preview_arts}</div>
<span class="three-preview-label"><i aria-hidden="true">✦</i> PRÉVIA DA PLACA</span>
<div class="three-selected-chip"><span data-selected-size>G</span><i aria-hidden="true">·</i><span data-selected-color>Preta</span></div>
<span class="visually-hidden" data-variant-status aria-live="polite">Placa G preta selecionada</span>
</figure>
<div class="three-option-panel">
<div><p class="three-kicker">1 · TAMANHO</p><div class="three-size-options" role="group" aria-label="Escolha o tamanho da placa">
<button class="three-size-option" type="button" data-plate-size="M" aria-pressed="false"><span class="three-size-name">M</span><span class="three-size-description">64 × 100 × 4 mm · 80%</span><strong data-price="plate:M">Preço sob consulta</strong></button>
<button class="three-size-option" type="button" data-plate-size="G" aria-pressed="true"><span class="three-size-name">G</span><span class="three-size-description">80 × 125 × 5 mm · 100%</span><strong data-price="plate:G">Preço sob consulta</strong></button>
</div></div>
<div><p class="three-kicker">2 · COR</p><div class="three-color-options" role="group" aria-label="Escolha a cor da placa">
<button class="three-color-option" type="button" data-plate-color="branca" aria-label="Branca" aria-pressed="false"><i class="three-swatch white" aria-hidden="true"></i>Branca</button>
<button class="three-color-option" type="button" data-plate-color="preta" aria-label="Preta" aria-pressed="true"><i class="three-swatch black" aria-hidden="true"></i>Preta</button>
</div></div>
<div class="three-customization" aria-labelledby="customization-title"><p class="three-kicker" id="customization-title">3 · PERSONALIZAÇÃO</p>
<div class="three-custom-grid">
<div class="three-upload-control"><label class="three-upload-label" for="custom-logo">Logo do seu negócio</label><input id="custom-logo" class="three-file-input" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" data-custom-file="logo"><small data-custom-name="logo">Escolha a imagem da logo · PNG, JPG, WEBP ou SVG · até 5 MB</small><button class="three-file-clear" type="button" data-clear-custom="logo" hidden>Remover logo</button></div>
<div class="three-upload-control"><label class="three-upload-label" for="custom-qr">Imagem do QR Code (opcional)</label><input id="custom-qr" class="three-file-input" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" data-custom-file="qr"><small data-custom-name="qr">Se quiser o QR, escolha a imagem · até 5 MB</small><button class="three-file-clear" type="button" data-clear-custom="qr" hidden>Remover QR</button></div>
</div>
<label class="three-qr-toggle"><input type="checkbox" data-preview-qr-toggle checked><span><strong>Incluir QR Code (opcional)</strong><small>Sem imagem enviada, a prévia mostra um QR ilustrativo, não escaneável.</small></span></label>
<p class="three-custom-note">Os arquivos aparecem apenas na prévia deste navegador. Envie a logo e, se quiser, o QR pelo WhatsApp após revisar o pedido.</p>
<p class="three-custom-status" data-custom-status role="status" aria-live="polite"></p></div>
<div class="three-included"><span class="three-nfc-icon" aria-hidden="true">)))</span><span><strong>NFC incluso</strong><small>O QR Code é opcional.</small></span></div>
<a class="btn three-order-button" data-order-variant href="produtos/placa-avaliacao-google.html?v=G-preta#pedido">Pedir esta placa <span aria-hidden="true">↗</span></a>
<p class="three-order-note">Prazo, dimensões e disponibilidade são confirmados antes do pedido.</p>
</div></div>
</div></section>
{nfc_demo()}''',
         cur="3d", forms=False, page_css="assets/css/pages/3d.css")
    # Produto
    arts = ""
    for s, c, n in VARIANTS:
        hid = "" if (s, c) == ("M", "branca") else " hidden"
        arts += f'<div data-variant-art="{s}-{c}"{hid}>{art(plate(s, c), f"Imagem ilustrativa: {s} {c}", f"{s}-{c}", f"Placa {s} {c}")}</div>'
    page("produtos/placa-avaliacao-google.html", "Placa de avaliação do Google | AxoLabz 3D",
         "Placa impressa em 3D para avaliação no Google, com NFC incluso e QR Code opcional. Tamanhos M e G, branca ou preta.",
         head("Placa de avaliação do Google", "Impressa em 3D, sob encomenda, para o seu cliente deixar uma avaliação com um toque.", [("../index.html", "Início"), ("../3d.html", "3D")]) +
         f'''<section><div class="wrap split top"><div>{arts}</div>
<div><h2>Detalhes</h2>
<dl class="rev-list"><dt>Variante</dt><dd id="chosen">Escolha uma variante</dd><dt>Dimensões</dt><dd id="plate-dim">A confirmar</dd>
<dt>NFC</dt><dd>Incluso</dd><dt>QR Code</dt><dd>Adicional opcional</dd><dt>Preço</dt><dd id="plate-price">Escolha o tamanho para ver o preço</dd></dl>
<p>Placa impressa em 3D para avaliação no Google. O NFC já está incluso. O QR Code é um recurso adicional, opcional.</p>
<div class="notice"><p><strong>Fabricação sob encomenda.</strong> O prazo será confirmado pelo WhatsApp, junto com a disponibilidade e as condições de pagamento.</p></div></div></div></section>
''' + nfc_demo() + f'''<section class="alt" id="pedido"><div class="wrap"><h2>Peça sua placa</h2><p>Escolha a variante e preencha os dados. Você revisa tudo antes de abrir o WhatsApp.</p>{pedido_form()}</div></section>''',
         cur="3d", exact=False, forms=True, float_=False)

    # Sobre
    vals = [("Inovação", "Buscamos soluções atuais e simples de usar."), ("Acessibilidade", "Explicamos tudo em linguagem simples e pensamos em soluções que cabem na realidade de pequenos negócios."),
            ("Agilidade", "Processo direto, com etapas claras e prazos combinados por escrito."), ("Qualidade", "Testamos e conferimos o trabalho antes de entregar."),
            ("Transparência", "Escopo, preço e prazo definidos antes do início."), ("Compromisso", "Cumprimos o que foi combinado e avisamos quando algo muda.")]
    page("sobre.html", "Sobre | AxoLabz", "Conheça a AxoLabz, sua forma de trabalhar e seus valores.",
         head("Sobre a AxoLabz", "Uma empresa de tecnologia com duas divisões e um jeito simples de trabalhar.") +
         f'''<section><div class="wrap split top"><div><h2>Quem somos</h2>
<p>A AxoLabz é uma empresa de tecnologia com duas divisões: a Digital, que cria sites e catálogos, e a 3D, que fabrica placas de avaliação do Google sob encomenda.</p>
<p>Atendemos pequenos negócios, comerciantes, profissionais autônomos e empresas locais, com inovação, acessibilidade e agilidade, sustentadas por qualidade, transparência e compromisso.</p></div>
<div><h2>O que fazemos</h2><ul class="tick"><li><a href="digital.html">AxoLabz Digital</a>: landing pages, sites, catálogos e lojas virtuais</li><li><a href="3d.html">AxoLabz 3D</a>: placas de avaliação com NFC incluso</li></ul></div></div></section>
<section class="alt"><div class="wrap"><h2>Nosso processo</h2><p class="lead" style="margin-bottom:2rem">Cada trabalho segue as mesmas seis etapas.</p>{steps_html()}</div></section>
<section><div class="wrap"><h2>Valores</h2><div class="values">{"".join(f"<div><strong>{n}</strong><p>{d}</p></div>" for n, d in vals)}</div></div></section>
<section class="alt"><div class="wrap"><h2>Projetos reais</h2><p>A galeria será ampliada conforme os trabalhos forem concluídos e autorizados para divulgação.</p>
<div class="cards">{"".join('<div class="slot"><p>Espaço reservado para um projeto real</p></div>' for _ in range(3))}</div></div></section>''', cur="sobre")

    # Contato
    page("contato.html", "Contato e orçamento | AxoLabz", "Fale com a AxoLabz pelo WhatsApp e peça um orçamento de serviços digitais.",
         head("Contato", "O atendimento comercial acontece pelo WhatsApp. Prepare sua mensagem aqui e revise antes de abrir a conversa.") +
         f'''<section><div class="wrap"><h2>Fale com a AxoLabz</h2>
{NO_WA}
<div class="actions" style="margin-top:0"><a class="btn" data-wa href="#aviso-whatsapp">Falar no WhatsApp</a><a class="btn line" data-ig-item data-ig href="#" rel="noopener">Ver o Instagram</a></div>
<p class="muted" data-city data-prefix="Cidade: " style="margin-top:1rem"></p>
<p class="muted" style="margin-top:1rem">Para pedir uma placa 3D, escolha a variante na <a href="produtos/placa-avaliacao-google.html">página da placa</a>.</p></div></section>
<section class="alt" id="orcamento"><div class="wrap"><h2>Orçamento de serviços digitais</h2>
<p>Preencha os dados, revise o resumo e só então abra o WhatsApp. O formulário não envia nada sozinho nem guarda suas informações.</p>{DIGITAL_FORM}</div></section>''',
         cur="contato", forms=True, float_=False)

    # Condições
    dig = ["O orçamento será enviado por escrito pelo WhatsApp.", "O escopo, o preço, o prazo, os entregáveis e as condições de pagamento são aprovados antes do início.",
           "O projeto começa após a aprovação e o pagamento inicial acordado.", "Uma rodada consolidada de revisão está incluída, conforme o escopo contratado.",
           "Revisões extras, novas funcionalidades e mudanças fora do escopo podem gerar cobrança adicional.", "O prazo é acordado por escrito, considerando a complexidade e a disponibilidade.",
           "Os arquivos finais e as instruções de entrega são fornecidos conforme o serviço contratado.", "Domínio e hospedagem ficam em nome do cliente e são pagos por ele. A AxoLabz pode orientar a configuração."]
    td = ["As placas são feitas sob encomenda.", "Prazo e disponibilidade são confirmados pelo WhatsApp.", "Retirada e entrega local são priorizadas.",
          "Envio para outras cidades está sujeito a consulta.", "Os custos de entrega ou envio são informados antes da confirmação.",
          "O pagamento pode ser feito por Pix ou por outras opções combinadas para cada pedido.", "O pedido só é considerado confirmado após a validação dos dados e a aceitação das condições pela AxoLabz."]
    page("condicoes.html", "Condições comerciais | AxoLabz", "Condições comerciais dos serviços digitais e das placas 3D da AxoLabz.",
         head("Condições comerciais", "Como funcionam orçamentos, prazos, pagamentos e pedidos.") +
         f'''<section><div class="wrap split top"><div><h2>Serviços digitais</h2><ul class="tick">{lis(dig)}</ul></div>
<div><h2>Produtos 3D</h2><ul class="tick">{lis(td)}</ul></div></div></section>''')

    # Privacidade
    page("privacidade.html", "Aviso de privacidade | AxoLabz", "Como os formulários do site da AxoLabz tratam as informações que você digita.",
         head("Aviso de privacidade", "Em linguagem simples: o que você digita, para onde vai e o que o site não faz.") +
         '''<section><div class="wrap" style="max-width:820px">
<h2>Quais informações você digita</h2><p>Os formulários pedem dados como tipo de projeto, nome do negócio ou estabelecimento, funcionalidades desejadas, variante da placa, link de avaliação do Google e observações. Você decide o que escrever.</p>
<h2>Como os formulários funcionam</h2><p>Os formulários funcionam no seu navegador. O site não envia esses dados a um servidor da AxoLabz e não guarda pedidos em banco de dados, cookies ou no armazenamento do navegador.</p>
<h2>Prévia da placa</h2><p>As imagens de logo e QR Code escolhidas no configurador 3D são lidas no navegador para a prévia visual. O site não as envia nem as armazena. Para fazer um pedido, envie os arquivos pelo WhatsApp depois de revisar a solicitação.</p>
<h2>Quando os dados saem do seu navegador</h2><p>As informações entram em uma mensagem de WhatsApp apenas quando você revisa e confirma a abertura do WhatsApp. Antes disso, você pode ler e copiar a mensagem.</p>
<h2>O WhatsApp é um serviço externo</h2><p>Ao abrir o WhatsApp, você passa a usar um serviço de terceiros, sujeito às políticas dele. A AxoLabz só recebe a mensagem se você a enviar.</p>
<h2>Hospedagem</h2><p>O site é hospedado no GitHub Pages, que pode registrar dados técnicos de acesso, como o endereço IP, conforme as políticas do GitHub. As fontes e demais arquivos do site são servidos pelo próprio site.</p>
<h2>O que o site não usa</h2><p>Neste lançamento, o site não usa analytics, pixels de publicidade nem outros rastreadores. Se algum for incluído no futuro, a necessidade e a privacidade serão avaliadas antes e este aviso será atualizado.</p>
<h2>Dúvidas sobre privacidade</h2><p>Fale com a AxoLabz pela <a href="contato.html">página de contato</a>.</p>
</div></section>''')

# ---------- escrita ----------
def write(path, text):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    build_pages()
    for p, t in PAGES.items():
        write(p, t)
    write("assets/img/logo.svg", logo_file())
    write("assets/img/logo-branca.svg", logo_file(color="#ffffff", gill="#5cd6e3"))
    write("assets/img/logo-compacta.svg", logo_file(True))
    write("assets/img/favicon.svg", FAVICON)
    write(".nojekyll", "")
    for f in ("archivo-latin-wdth-normal.woff2", "figtree-latin-wght-normal.woff2"):
        src = os.path.join(FONTS, f)
        dst = os.path.join(OUT, "assets/fonts", f)
        if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
    print(len(PAGES), "páginas geradas em", OUT)

if __name__ == "__main__":
    main()

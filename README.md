# Site AxoLabz

Site estático (HTML, CSS e JavaScript puros) pronto para o GitHub Pages. Sem backend, banco de dados, analytics ou rastreadores.

## Publicar no GitHub Pages
1. Crie um repositório e envie o conteúdo desta pasta para a raiz (inclua o arquivo `.nojekyll`).
2. Em Settings > Pages, escolha a branch `main` e a pasta `/ (root)`.
3. Todos os caminhos são relativos, então funciona em `usuario.github.io/repositorio/`.

## Onde editar (tudo em `assets/js/config.js`)
WhatsApp, Instagram, cidade, preços dos serviços digitais, preços das placas M e G, dimensões, preço do QR Code adicional e fotos reais das placas.
Valores vazios não aparecem: o site mostra "a confirmar" ou "sob consulta" e esconde links sem destino.

Para trocar uma foto, salve o arquivo em `assets/img/` e informe o caminho em `photos` (ex.: `"assets/img/placa-m-branca.webp"`).

## Textos e páginas
`tools/build.py` gera todas as páginas (identidade visual inspirada em Infinite Machine, de David McGillivray, como referência). Para mudar textos, edite o arquivo e rode `python3 tools/build.py` na raiz do projeto. Os estilos compartilhados ficam em `assets/css/style.css`; estilos específicos de páginas ficam em `assets/css/pages/`.

## Pendências antes de publicar
- Número oficial do WhatsApp
- URL oficial do Instagram
- Cidade da empresa, se for divulgada
- Preços finais das placas M e G (o NFC já está incluso)
- Preços iniciais dos serviços digitais
- Preço e escopo definitivos da manutenção
- Preço e condições do QR Code adicional
- Fotos reais das placas M e G
- Dimensões e especificações verificadas
- Revisão final de Condições comerciais e Aviso de privacidade

## Organização do projeto
- `tools/build.py` gera as 13 páginas e os arquivos de identidade visual.
- `assets/js/config.js` concentra os dados comerciais; `assets/js/` contém navegação, formulários e animações.
- `assets/css/style.css` define o sistema compartilhado e `assets/css/pages/` guarda ajustes isolados por página.
- O HTML é gerado pelo build; altere os textos em `tools/build.py` e regenere o site.

## Interações modernas
A direção visual combina um palco escuro na home com conteúdo em branco e cinza-claro e rodapé escuro. A página inicial inclui o logotipo ampliado, uma prévia interativa da placa (tamanhos M/G e cores branca/preta), animações 3D e o botão "Pedir esta placa", que leva a variante escolhida ao formulário. O traço de rolagem é decorativo e oculto para leitores de tela. As animações respeitam prefers-reduced-motion; os controles da placa continuam disponíveis.

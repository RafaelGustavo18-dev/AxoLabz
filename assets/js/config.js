/*
  AxoLabz — CONFIGURAÇÃO COMERCIAL (único lugar para editar dados do negócio).
  Valores vazios (""), null ou inválidos NÃO aparecem no site:
  o site mostra "a confirmar" / "sob consulta" e esconde links sem destino.
*/
window.AXO_CONFIG = {
  // Número do WhatsApp com DDI+DDD, só dígitos. Ex.: "5544999999999"
  whatsapp: "",

  // URL oficial do Instagram, começando com https://instagram.com/ ou https://www.instagram.com/
  instagram: "",

  // Cidade da empresa. Deixe vazio para não exibir.
  city: "",

  // Preços iniciais dos serviços digitais, em número (ex.: 890). null = "Valor a confirmar".
  // Loja virtual é sempre sob consulta; manutenção é definida na proposta.
  digitalPrices: {
    "landing-page": null,
    "site-institucional": null,
    "catalogo-whatsapp": null,
    "manutencao": null
  },

  // Placas 3D: preço por tamanho (a cor não altera o preço) e dimensões verificadas (texto, ex.: "10 x 15 cm").
  // O NFC já está incluso no preço da placa.
  plates: {
    M: { price: null, dimensions: null },
    G: { price: null, dimensions: null }
  },

  // Preço do QR Code adicional (opcional). null = "Valor a confirmar".
  qrAddonPrice: null,

  // Fotos reais por variante. Caminho a partir da raiz do site. Ex.: "assets/img/placa-m-branca.webp"
  // Enquanto for null, o site mostra uma ilustração identificada como "Imagem ilustrativa".
  photos: {
    "M-branca": null,
    "M-preta": null,
    "G-branca": null,
    "G-preta": null
  }
};

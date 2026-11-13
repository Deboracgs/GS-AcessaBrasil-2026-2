# AcessaBrasil · Landing Page (Front-end Design)

Global Solution 2026.2 · CitizenTech · Prof. Fábio Alencar

Landing page do AcessaBrasil, o mapa colaborativo de acessibilidade que começa pelo Centro do Rio de Janeiro.

Repositório: [AcessaBrasil no GitHub](https://github.com/Deboracgs/GS-AcessaBrasil-2026-2)

## Como abrir

Abra o arquivo `index.html` no navegador (Chrome, Edge ou Firefox). O mapa precisa de internet para carregar a biblioteca Leaflet e os tiles HOT hospedados pelo OpenStreetMap França; o restante da página funciona offline.

## Estrutura

```
frontend-web-development/
├── index.html          estrutura da página (HTML)
├── css/style.css       estilos, modo escuro e versão para celular (CSS)
├── js/script.js        interações (JavaScript, disciplina de Web Development)
├── images/             logo, ilustração e ícones das categorias (SVG criados pela equipe)
└── integrantes.txt
```

## Requisitos atendidos

| Requisito                   | Onde está                                                                 |
| --------------------------- | ------------------------------------------------------------------------- |
| Menu de navegação funcional | Cabeçalho fixo com links âncora; vira menu "hambúrguer" no celular        |
| 5 seções de conteúdo        | Início, O problema, Mapa, Como funciona, Avaliar local, Equipe (6 seções) |
| Rodapé padronizado          | Marca, links rápidos, créditos da GS e do mapa                            |
| Imagens e ícones            | Pasta `images/` com logo, ilustração e 9 ícones de categorias             |
| HTML e CSS separados        | `index.html` e `css/style.css`                                            |

## Decisões de design

- Paleta verde (acessibilidade, "pode passar") com cores de estado verde, amarelo e vermelho, sempre acompanhadas de texto para não depender só da cor.
- Contraste alto, foco visível no teclado (contorno amarelo), link "Pular para o conteúdo" e botões A− / A+ para o tamanho do texto.
- Layout responsivo em grid, com uma coluna em telas pequenas.
- Categorias do mapa: cadeira de rodas, deficiência visual, Libras, banheiro acessível, semáforo sonoro, ambiente amigável para autismo (TEA), vaga para idoso e vaga PcD/TEA, além do filtro de lugares calmos (ruído até 55 dB).

## Equipe

Débora Gonçalves da Silva (RM575926), Pedro Paulo Carvalho Coutinho (RM575957), Vanessa Santos Martins de Lima Nascimento (RM576450).

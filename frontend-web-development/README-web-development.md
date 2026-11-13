# AcessaBrasil · Interatividade e Funcionalidades Dinâmicas (Web Development)

Global Solution 2026.2 · CitizenTech · Prof. Igor Araújo

Repositório: [AcessaBrasil no GitHub](https://github.com/Deboracgs/GS-AcessaBrasil-2026-2)

O JavaScript do AcessaBrasil fica em [`js/script.js`](js/script.js). Este documento reúne a documentação pedida pela disciplina.

## Como testar

1. Abra `index.html` no navegador (com internet, para o mapa).
2. Use as interações abaixo.

## Interações implementadas

| #   | Interação                                                                                                                                                   | Conceitos usados                                                                           |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --- | --- |
| 1   | **Modo claro / escuro** no botão ☾/☀ do cabeçalho, com a escolha salva no navegador                                                                         | `addEventListener`, `classList.toggle`, operador ternário, `localStorage` com `try/catch`  |
| 2   | **Filtros do mapa** por categoria (cadeira de rodas, visual, Libras, banheiro, semáforo sonoro, autismo, vaga idoso, vaga PcD/TEA) e por **lugares calmos** | `querySelectorAll`, `dataset`, `forEach`, condicionais, operadores lógicos `&&` e `        |     | `   |
| 3   | **Busca** por nome do local, com contador de resultados                                                                                                     | evento `input`, `toLowerCase`, `includes`, `if/else if/else`                               |
| 4   | **Simulador da calçada**: digita a largura e recebe LIVRE, ATENÇÃO ou BLOQUEADO (a mesma regra do Python e do ESP32)                                        | função `classificarLargura()`, `if/else if/else`, manipulação de classes e `innerHTML`     |
| 5   | **Semáforo sonoro**: botão "Pedir travessia" acende o verde, toca bipes rápidos e depois acelera os bipes antes de fechar                                   | `setTimeout`, `setInterval`, Web Audio API, funções                                        |
| 6   | **Avaliar um local**: formulário com validação que cria um novo pin no mapa e atualiza os indicadores                                                       | `preventDefault`, validação com condicionais, `push` em array, criação de elementos no DOM |
| 7   | **Tamanho do texto** A− / A+                                                                                                                                | variável CSS alterada por JavaScript, limites com operadores de comparação                 |
| 8   | **Menu mobile** que abre e fecha                                                                                                                            | `classList.toggle`, atributo `aria-expanded`                                               |

## Regras de decisão

| Medida                   | Faixas                                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| Largura livre da calçada | 120 cm ou mais = LIVRE · 90 a 119 = ATENÇÃO · menos de 90 = BLOQUEADO · 0 ou acima de 400 = INVÁLIDA    |
| Ruído do local           | até 55 dB = Calmo · 56 a 70 = Moderado · acima de 70 = Barulhento                                       |
| Pin do local             | 0 recursos = Sem acessibilidade (vermelho) · 1 ou 2 = Parcial (amarelo) · 3 ou mais = Acessível (verde) |

## Bibliotecas

- [Leaflet 1.9.4](https://leafletjs.com/) para desenhar o mapa, com tiles HOT do OpenStreetMap França, sem chave de API. Cada pin tem um link "Como chegar no Google Maps" que abre a rota a pé.

## Arquivos desta entrega

- `README-web-development.md` (este arquivo)
- `Integrantes.md`
- `AcessaBrasil-web.zip` (projeto completo)

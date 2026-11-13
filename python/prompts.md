# Registro de uso de IA (prompts.md)

A equipe usou IA generativa (Claude, da Anthropic) como copiloto para aprender e revisar o código, conforme os combinados da GS. Todas as linhas do `main.py` foram lidas e discutidas pela equipe, e cada integrante sabe explicar o programa.

> Revisem e completem este arquivo com os prompts que vocês realmente usaram, na ordem em que usaram.

## Prompts utilizados

**1. Definição das faixas**
> "Qual é a largura mínima de calçada para uma cadeira de rodas passar segundo a NBR 9050? Quero criar três faixas (livre, atenção, bloqueado) para classificar leituras de um sensor ultrassônico."

O que aproveitamos: a faixa livre mínima de 1,20 m e o módulo de referência de 0,80 m da cadeira de rodas. Daí vieram os limites de 120 cm e 90 cm.

**2. Estrutura do programa**
> "Monte um esqueleto em Python com menu em loop, lista de dicionários com 10 ou mais leituras simuladas e uma função de classificação com if/elif/else. Use só conceitos de primeiro semestre."

O que aproveitamos: a divisão em funções, uma por opção do menu.

**3. Entrada inválida**
> "Como impedir que o programa quebre quando o usuário digita letras onde deveria digitar um número?"

O que aproveitamos: a função `ler_numero()` com `try/except ValueError` dentro de um `while True`.

**4. Revisão**
> "Revise o código e aponte trechos difíceis de explicar para um professor de primeiro ano."

O que mudamos: removemos um trecho desnecessário dentro de `ler_numero()` e deixamos os comentários mais curtos.

## O que a IA não fez

A escolha do problema (acessibilidade no Centro do Rio), a definição do cidadão, os locais simulados e a integração com o sensor e com a página foram decisões da equipe.

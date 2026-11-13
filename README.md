# AcessaBrasil

> Global Solution 2026.2 · CitizenTech · Engenharia de Software 1º ano · FIAP Rio de Janeiro

Mapa colaborativo que mostra, com pins coloridos, quais lugares têm acessibilidade (rampa, elevador, piso tátil, Libras, banheiro adaptado, semáforo sonoro), vagas para idosos e para pessoas com deficiência ou autismo, e quais são calmos o bastante para quem tem sensibilidade a barulho. Também avisa se a calçada até o local está livre. O projeto começa pelo Centro do Rio de Janeiro.

## Ficha da CitizenTech

| Campo                      | Resposta da equipe                                                                                                                                                                                                                                                                                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nome da CitizenTech**    | AcessaBrasil                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Cidade e bairro**        | Rio de Janeiro, Centro (Carioca, Cinelândia, Praça XV e Praça Mauá)                                                                                                                                                                                                                                                                                                                                                       |
| **Cidadão beneficiado**    | Pessoas com deficiência física, visual ou auditiva, pessoas autistas (TEA) e suas famílias, idosos e quem anda com carrinho de bebê no Centro do Rio. Personas: Marcos, 34 anos, cadeirante; Ana, mãe do Theo, 8 anos, autista; Dona Lúcia, 72 anos, baixa visão.                                                                                                                                                         |
| **Problema, em uma frase** | Pessoas com deficiência, autistas e idosos saem de casa sem saber se o destino é acessível, se há vaga reservada, se o ambiente é barulhento demais ou se a calçada está livre, e só descobrem a barreira quando já estão na frente dela.                                                                                                                                                                                 |
| **Como funciona**          | Um semáforo sonoro de pedestres com ESP32 apita para guiar quem não enxerga e, com um sensor ultrassônico, mede a largura livre da rampa da faixa; o Python classifica as leituras de calçada (LIVRE, ATENÇÃO, BLOQUEADO) e de ruído (Calmo, Moderado, Barulhento) e gera o resumo; a página mostra o mapa com pins por categoria e o aviso para o cidadão.                                                               |
| **O que cada parte faz**   | veja a tabela abaixo                                                                                                                                                                                                                                                                                                                                                                                                      |
| **Link do repositório**    | [AcessaBrasil no GitHub](https://github.com/Deboracgs/GS-AcessaBrasil-2026-2)                                                                                                                                                                                                                                                                                                                                                                     |
| **Indicador de impacto**   | Percentual de locais mapeados com acessibilidade completa, número de lugares calmos mapeados e número de leituras de calçada em alerta por semana (meta: reduzir as leituras BLOQUEADO nos pontos monitorados).                                                                                                                                                                                                           |
| **ODS conectados**         | **ODS 10** (redução das desigualdades: dá autonomia de deslocamento a pessoas com deficiência), **ODS 11** (cidades sustentáveis, meta 11.2 e 11.7: transporte e espaços públicos acessíveis), **ODS 3** (saúde e bem-estar: menos quedas, travessias mais seguras e menos sobrecarga sensorial para pessoas autistas), **ODS 9** (infraestrutura e inovação: sensores de baixo custo que geram dados para a prefeitura). |

### Regra comum a todas as partes

A mesma regra de decisão aparece no sensor, no Python e no JavaScript. Ela se baseia na faixa livre mínima de 1,20 m para calçadas prevista na ABNT NBR 9050 e no módulo de referência de 0,80 m de uma cadeira de rodas.

| Largura livre medida | Estado           | Aviso para o cidadão                                           |
| -------------------- | ---------------- | -------------------------------------------------------------- |
| 120 cm ou mais       | LIVRE            | Calçada livre: passagem acessível para cadeira de rodas.       |
| de 90 a 119 cm       | ATENÇÃO          | Passagem estreita: siga com cuidado ou use a rota alternativa. |
| menos de 90 cm       | BLOQUEADO        | Calçada bloqueada: use a rota alternativa indicada no mapa.    |
| 0 ou acima de 400 cm | LEITURA INVÁLIDA | Leitura descartada, o sensor mede de novo.                     |

Para o ruído (pessoas autistas e com sensibilidade sensorial): até 55 dB = Calmo, 56 a 70 dB = Moderado, acima de 70 dB = Barulhento.

### Categorias do mapa

Cadeira de rodas (rampa ou elevador) · Deficiência visual (piso tátil, braille) · Libras · Banheiro acessível · Semáforo sonoro · Ambiente amigável para autismo (TEA) · Vaga para idoso · Vaga PcD/TEA · filtro de lugares calmos.

### O que cada parte faz

| Parte       | Disciplina                              | Pasta                                                                           | O que faz                                                                                                                                                                   |
| ----------- | --------------------------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lógica      | Computational Thinking with Python      | `python/`                                                                       | Classifica as leituras de calçada e de ruído e os locais, calcula média, maior valor e % em alerta, e gera o aviso.                                                         |
| Matemática  | Differentiated Problem Solving          | `python/`                                                                       | Faixas numéricas de largura da calçada e nível de ruído usadas nas classificações.                                                                                                                                             |
| Sensor      | Edge Computing & Computer Systems       | `edge-computing/`                                                               | Semáforo sonoro de pedestres com ESP32: botão de travessia, LEDs, buzzer com ritmos diferentes, LCD e sensor ultrassônico que avisa quando a rampa da faixa está bloqueada. |
| Interface   | Front-end Design                        | `frontend-web-development/`                                                     | Landing page com o mapa de pins, as categorias de acessibilidade e as seções do projeto.                                                                                    |
| Experiência | Software & Total Experience Design      | `software-design/`                                                              | Escopo, requisitos (RF, RNF, RN), backlog e priorização.                                                                                                                    |
| Interação   | Web Development                         | `frontend-web-development/` (código em `frontend-web-development/js/script.js`) | Filtros do mapa, busca, simulador de calçada, semáforo sonoro com som, formulário de avaliação, modo claro/escuro e ajuste de fonte.                                        |
| Pitch       | Storytelling & Inspiração Empreendedora | `storytelling/`                                                                 | Vídeo ainda não publicado.                                                                                                                                                  |

## Dados

Todos os locais, avaliações e leituras são **simulados** para o protótipo. Os nomes dos lugares são reais apenas para dar contexto ao mapa; as informações de acessibilidade atribuídas a eles não foram verificadas em campo e não devem ser usadas como informação oficial. Nenhum dado pessoal real é coletado.

## Equipe

| Nome completo                             | RM       |
| ----------------------------------------- | -------- |
| Débora Gonçalves da Silva                 | RM575926 |
| Pedro Paulo Carvalho Coutinho             | RM575957 |
| Vanessa Santos Martins de Lima Nascimento | RM576450 |

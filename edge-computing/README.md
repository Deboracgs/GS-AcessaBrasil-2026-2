# AcessaBrasil · Semáforo sonoro com monitor de rampa (Edge Computing)

Global Solution 2026.2 · CitizenTech IoT: Monitoramento Inteligente com Microcontrolador

## A ideia

| | |
|---|---|
| **Cidadão** | Pessoas cegas ou com baixa visão, cadeirantes e idosos que atravessam as ruas do Centro do Rio |
| **Problema em uma frase** | Quem não enxerga não sabe quando o sinal de pedestres abriu, e quem usa cadeira de rodas chega à faixa e encontra a rampa bloqueada por carro, moto ou entulho. |
| **Onde o dispositivo fica** | No poste do semáforo de pedestres, junto à botoeira, com o sensor ultrassônico apontado para a rampa da calçada |
| **ODS** | ODS 10 (redução das desigualdades), ODS 11 (meta 11.2: transporte seguro e acessível), ODS 3 (menos acidentes na travessia) |

O semáforo sonoro é comum em cidades de países como Japão, Austrália e Espanha: ele faz um tom lento quando o sinal está fechado para o pedestre (para a pessoa cega encontrar o botão), bipes rápidos quando abre e bipes ainda mais rápidos quando vai fechar. O AcessaBrasil junta isso a um monitor da rampa, e tudo funciona sem internet.

## Como montar no Wokwi

1. Acesse [wokwi.com](https://wokwi.com), entre com a conta da equipe e crie um projeto **ESP32**.
2. Na aba `sketch.ino`, cole o conteúdo de `sketch.ino` desta pasta.
3. Na aba `diagram.json`, cole o conteúdo de `diagram.json`.
4. Clique no **+** ao lado das abas, crie o arquivo `libraries.txt` e cole o conteúdo de `libraries.txt` (biblioteca LiquidCrystal I2C).
5. Rode a simulação. Arraste os componentes para deixar os fios sem cruzamentos desnecessários e salve.
6. Clique em **Share** e copie o link público para a entrega.

## Componentes e por que estão ali

| Componente | Pino ESP32 | Função |
|---|---|---|
| ESP32 DevKit C | | Cérebro do dispositivo, decide sozinho na borda |
| Sensor ultrassônico HC-SR04 | TRIG 5, ECHO 18 | Mede a largura livre da rampa da faixa |
| Botão azul (botoeira) | 4 (INPUT_PULLUP) | O pedestre pede a travessia |
| LED vermelho + 220 Ω | 25 | "Pare" para o pedestre |
| LED verde + 220 Ω | 26 | "Atravesse" (pisca quando vai fechar) |
| LED amarelo + 220 Ω | 27 | Rampa bloqueada (aceso) ou em atenção / sensor com falha (piscando) |
| Buzzer | 13 | Ritmo de bipes de cada estado e alerta grave da rampa |
| LCD 16x2 I2C | SDA 21, SCL 22 | Mostra o estado do semáforo, o tempo restante e a largura da rampa |
| Chave deslizante | 19 | Só para teste: simula o sensor desconectado para demonstrar a leitura inválida |

## Lógica de borda

**Semáforo (4 estados):**

| Estado | Luz | Som | Duração |
|---|---|---|---|
| AGUARDE | vermelho | 1 bipe de 440 Hz a cada 1,5 s (tom localizador) | até apertar o botão |
| PEDIDO | vermelho | tom localizador | 3 s |
| ATRAVESSE | verde fixo | bipe de 880 Hz a cada 0,3 s | 10 s, com contagem no LCD |
| ENCERRANDO | verde piscando | bipe de 880 Hz a cada 0,12 s | 5 s |

**Rampa (mesmas faixas do Python e do site):**

| Largura livre (média) | Estado | Resposta |
|---|---|---|
| 120 cm ou mais | LIVRE | LED amarelo apagado |
| 90 a 119 cm | ATENCAO | LED amarelo piscando |
| menos de 90 cm | BLOQUEADA | LED amarelo aceso, alerta grave de 220 Hz a cada 3 s com o sinal fechado |
| 0 ou acima de 400 cm | INVÁLIDA | leitura descartada; após 5 seguidas o LCD mostra "SENSOR?" |

**Por que esses limites:** 1,20 m é a faixa livre mínima de calçada da ABNT NBR 9050; 0,80 m é a largura do módulo de referência de uma cadeira de rodas, então abaixo de 90 cm não há folga segura; 400 cm é o alcance do HC-SR04.

**Suavização:** média móvel das 5 últimas leituras válidas, para que uma pessoa passando na frente do sensor por um instante não dispare o alerta.

**Código:** constantes para pinos, limites e tempos; funções separadas (`atualizarRampa`, `atualizarSemaforo`, `atualizarLuzes`, `atualizarSom`, `atualizarLcd`); tudo com `millis()`, sem `delay()` no loop; saída no Serial Monitor a cada segundo.

## Roteiro do vídeo (até 5 min)

| Tempo | Quem fala | O que mostrar |
|---|---|---|
| 0:00 a 0:50 | Integrante 1 | **A ideia:** quem é o cidadão (pessoa cega, cadeirante, idoso), o problema em uma frase, onde o dispositivo fica (poste do semáforo) e os ODS 3, 10 e 11. |
| 0:50 a 1:50 | Integrante 2 | **O circuito:** passar o mouse por cada componente da tabela acima e dizer por que ele está ali. |
| 1:50 a 3:00 | Integrante 3 | **A lógica:** mostrar no código as constantes de limite, a função `classificarRampa()` com if/else, a média móvel em `adicionarLeitura()` e a máquina de estados em `atualizarSemaforo()`. |
| 3:00 a 4:40 | Todos | **Simulação comentada:** (1) estado AGUARDE com o tom lento; (2) apertar o botão: PEDIDO, ATRAVESSE com contagem e bipes rápidos, ENCERRANDO com verde piscando; (3) clicar no sensor e baixar a distância para 100 cm: ATENCAO; para 60 cm: BLOQUEADA com alerta grave; (4) ligar a chave de falha: leituras inválidas no Serial Monitor e "SENSOR?" no LCD; (5) desligar a chave e voltar para 150 cm: LIVRE. |
| 4:40 a 5:00 | Integrante 1 | Fechamento: como esse dispositivo alimenta o mapa do AcessaBrasil. |

## Equipe

Os nomes também estão no cabeçalho do `sketch.ino`.

| Nome completo | RM |
|---|---|
| Débora Gonçalves da Silva | RM575926 |
| Pedro Paulo Carvalho Coutinho | RM575957 |
| Vanessa Santos Martins de Lima Nascimento | RM576450 |

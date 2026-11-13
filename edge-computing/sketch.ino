/* =============================================================
   AcessaBrasil · Semáforo sonoro de pedestres com monitor de rampa
   Global Solution 2026.2 · Edge Computing & Computer Systems
   FIAP Rio de Janeiro · Engenharia de Software 1º ano

   Equipe:
     Débora Gonçalves da Silva                  RM575926
     Pedro Paulo Carvalho Coutinho              RM575957
     Vanessa Santos Martins de Lima Nascimento  RM576450

   O que faz (sem internet, decide sozinho):
   1) Semáforo sonoro: a pessoa aperta o botão (botoeira) e o
      semáforo de pedestres passa por 4 estados, cada um com luz e
      ritmo de bipe diferentes, para guiar quem não enxerga.
   2) Monitor da rampa: o sensor ultrassônico, preso no poste e
      apontado para a rampa da faixa, mede a largura livre.
      Se um carro, moto ou entulho bloqueia a rampa, o LED amarelo
      acende, o LCD avisa e o buzzer dá um alerta grave.

   Faixas (as mesmas do Python e do JavaScript do AcessaBrasil):
     >= 120 cm  LIVRE      faixa livre mínima da ABNT NBR 9050
     90 a 119   ATENCAO    cadeira de rodas (80 cm) passa com dificuldade
     < 90 cm    BLOQUEADO  cadeira de rodas não passa
     0 ou > 400 INVALIDA   fora do alcance do HC-SR04, leitura descartada
   ============================================================= */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---------- Pinos ----------
const int PINO_TRIG = 5;
const int PINO_ECHO = 18;
const int PINO_LED_VERMELHO = 25;   // pedestre: pare
const int PINO_LED_VERDE = 26;      // pedestre: atravesse
const int PINO_LED_AMARELO = 27;    // rampa com problema
const int PINO_BUZZER = 13;
const int PINO_BOTAO = 4;           // botoeira do pedestre
const int PINO_TESTE_FALHA = 19;    // chave deslizante: simula o sensor desconectado (só para teste no Wokwi)

// ---------- Limites da rampa (cm) ----------
const float LIMITE_LIVRE = 120.0;
const float LIMITE_ATENCAO = 90.0;
const float LEITURA_MAXIMA = 400.0;
const int TAMANHO_MEDIA = 5;            // suavização: média das 5 últimas leituras válidas
const int MAX_INVALIDAS_SEGUIDAS = 5;   // depois disso, indica falha do sensor

// ---------- Tempos do semáforo (ms) ----------
const unsigned long TEMPO_PEDIDO = 3000;      // espera depois de apertar o botão
const unsigned long TEMPO_TRAVESSIA = 10000;  // verde fixo
const unsigned long TEMPO_ENCERRANDO = 5000;  // verde piscando
const unsigned long INTERVALO_LEITURA = 250;  // leitura do sensor 4 vezes por segundo
const unsigned long INTERVALO_LCD = 500;
const unsigned long INTERVALO_SERIAL = 1000;

// Ritmo dos bipes de cada estado (ms entre bipes) e frequência (Hz)
const unsigned long BIPE_LOCALIZADOR = 1500;  // tom lento: ajuda a achar o botão
const unsigned long BIPE_TRAVESSIA = 300;     // bipes rápidos: pode atravessar
const unsigned long BIPE_ENCERRANDO = 120;    // bipes muito rápidos: vai fechar
const int FREQ_LOCALIZADOR = 440;
const int FREQ_TRAVESSIA = 880;
const int FREQ_ALERTA_RAMPA = 220;            // som grave e diferente para a rampa bloqueada

// ---------- Estados ----------
enum EstadoSemaforo { AGUARDANDO, PEDIDO, TRAVESSIA, ENCERRANDO };
enum EstadoRampa { RAMPA_LIVRE, RAMPA_ATENCAO, RAMPA_BLOQUEADA, RAMPA_INVALIDA };

EstadoSemaforo estadoSemaforo = AGUARDANDO;
EstadoRampa estadoRampa = RAMPA_LIVRE;

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ---------- Variáveis de controle ----------
unsigned long inicioEstado = 0;
unsigned long ultimoBipe = 0;
unsigned long ultimaLeitura = 0;
unsigned long ultimoLcd = 0;
unsigned long ultimoSerial = 0;
unsigned long ultimoAlertaRampa = 0;

float leituras[TAMANHO_MEDIA];
int indiceLeitura = 0;
int quantidadeLeituras = 0;
int invalidasSeguidas = 0;
float larguraMedia = 0;
float ultimaLeituraBruta = 0;

bool botaoAnterior = HIGH;

// Declarações antecipadas (funções usadas antes de serem escritas)
const char* nomeSemaforo();
const char* nomeRampa();

// =============================================================
// Sensor ultrassônico
// =============================================================
float medirDistanciaCm() {
  // Modo de teste: com a chave ligada, o sensor "não responde" (eco ausente = 0 cm)
  if (digitalRead(PINO_TESTE_FALHA) == HIGH) return 0;
  digitalWrite(PINO_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PINO_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PINO_TRIG, LOW);
  // timeout de 30 ms: se não houver eco, devolve 0 (leitura inválida)
  unsigned long duracao = pulseIn(PINO_ECHO, HIGH, 30000);
  return duracao * 0.0343 / 2.0;
}

bool leituraValida(float cm) {
  return cm > 0 && cm <= LEITURA_MAXIMA;
}

// Guarda a leitura válida e recalcula a média móvel (suavização)
void adicionarLeitura(float cm) {
  leituras[indiceLeitura] = cm;
  indiceLeitura = (indiceLeitura + 1) % TAMANHO_MEDIA;
  if (quantidadeLeituras < TAMANHO_MEDIA) quantidadeLeituras++;

  float soma = 0;
  for (int i = 0; i < quantidadeLeituras; i++) soma += leituras[i];
  larguraMedia = soma / quantidadeLeituras;
}

EstadoRampa classificarRampa(float largura) {
  if (largura >= LIMITE_LIVRE) {
    return RAMPA_LIVRE;
  } else if (largura >= LIMITE_ATENCAO) {
    return RAMPA_ATENCAO;
  } else {
    return RAMPA_BLOQUEADA;
  }
}

void atualizarRampa() {
  ultimaLeituraBruta = medirDistanciaCm();
  if (leituraValida(ultimaLeituraBruta)) {
    invalidasSeguidas = 0;
    adicionarLeitura(ultimaLeituraBruta);
    estadoRampa = classificarRampa(larguraMedia);
  } else {
    // leitura inválida: descarta e mantém a decisão anterior
    invalidasSeguidas++;
    if (invalidasSeguidas >= MAX_INVALIDAS_SEGUIDAS) {
      estadoRampa = RAMPA_INVALIDA;
    }
  }
}

// =============================================================
// Semáforo
// =============================================================
void mudarEstado(EstadoSemaforo novo) {
  estadoSemaforo = novo;
  inicioEstado = millis();
  ultimoBipe = 0;  // força o primeiro bipe do novo estado
  Serial.print(">> Semaforo: ");
  Serial.println(nomeSemaforo());
}

const char* nomeSemaforo() {
  switch (estadoSemaforo) {
    case AGUARDANDO: return "AGUARDE";
    case PEDIDO:     return "PEDIDO";
    case TRAVESSIA:  return "ATRAVESSE";
    default:         return "ENCERRANDO";
  }
}

const char* nomeRampa() {
  switch (estadoRampa) {
    case RAMPA_LIVRE:     return "LIVRE";
    case RAMPA_ATENCAO:   return "ATENCAO";
    case RAMPA_BLOQUEADA: return "BLOQUEADA";
    default:              return "SENSOR?";
  }
}

bool botaoApertado() {
  bool atual = digitalRead(PINO_BOTAO);
  bool apertou = (botaoAnterior == HIGH && atual == LOW);  // detecta a borda de descida
  botaoAnterior = atual;
  return apertou;
}

void atualizarSemaforo() {
  unsigned long agora = millis();
  unsigned long tempoNoEstado = agora - inicioEstado;

  if (estadoSemaforo == AGUARDANDO) {
    if (botaoApertado()) mudarEstado(PEDIDO);
  } else if (estadoSemaforo == PEDIDO) {
    botaoApertado();  // ignora novos toques
    if (tempoNoEstado >= TEMPO_PEDIDO) mudarEstado(TRAVESSIA);
  } else if (estadoSemaforo == TRAVESSIA) {
    botaoApertado();
    if (tempoNoEstado >= TEMPO_TRAVESSIA) mudarEstado(ENCERRANDO);
  } else {
    botaoApertado();
    if (tempoNoEstado >= TEMPO_ENCERRANDO) mudarEstado(AGUARDANDO);
  }
}

// Luzes: cada estado tem uma combinação diferente
void atualizarLuzes() {
  bool vermelho = (estadoSemaforo == AGUARDANDO || estadoSemaforo == PEDIDO);
  bool verde = (estadoSemaforo == TRAVESSIA);
  if (estadoSemaforo == ENCERRANDO) {
    verde = ((millis() / 250) % 2 == 0);  // pisca 2 vezes por segundo
  }
  digitalWrite(PINO_LED_VERMELHO, vermelho);
  digitalWrite(PINO_LED_VERDE, verde);

  // Amarelo: aceso se a rampa está bloqueada, piscando em atenção ou falha do sensor
  bool amarelo = false;
  if (estadoRampa == RAMPA_BLOQUEADA) {
    amarelo = true;
  } else if (estadoRampa == RAMPA_ATENCAO || estadoRampa == RAMPA_INVALIDA) {
    amarelo = ((millis() / 500) % 2 == 0);
  }
  digitalWrite(PINO_LED_AMARELO, amarelo);
}

// Som: ritmo diferente em cada estado
void atualizarSom() {
  unsigned long agora = millis();
  unsigned long intervalo;
  int frequencia;

  if (estadoSemaforo == TRAVESSIA) {
    intervalo = BIPE_TRAVESSIA;
    frequencia = FREQ_TRAVESSIA;
  } else if (estadoSemaforo == ENCERRANDO) {
    intervalo = BIPE_ENCERRANDO;
    frequencia = FREQ_TRAVESSIA;
  } else {
    intervalo = BIPE_LOCALIZADOR;
    frequencia = FREQ_LOCALIZADOR;
  }

  if (ultimoBipe == 0 || agora - ultimoBipe >= intervalo) {
    tone(PINO_BUZZER, frequencia, 60);
    ultimoBipe = agora;
  }

  // Alerta extra da rampa bloqueada: som grave a cada 3 s,
  // só quando o semáforo está fechado para não confundir a travessia
  if (estadoRampa == RAMPA_BLOQUEADA && estadoSemaforo == AGUARDANDO &&
      agora - ultimoAlertaRampa >= 3000 && agora - ultimoBipe > 200) {
    tone(PINO_BUZZER, FREQ_ALERTA_RAMPA, 400);
    ultimoAlertaRampa = agora;
    ultimoBipe = agora;
  }
}

void atualizarLcd() {
  lcd.setCursor(0, 0);
  if (estadoSemaforo == AGUARDANDO) {
    lcd.print("AGUARDE  Aperte ");
  } else if (estadoSemaforo == PEDIDO) {
    lcd.print("PEDIDO   Aguarde");
  } else if (estadoSemaforo == TRAVESSIA) {
    int restante = (TEMPO_TRAVESSIA - (millis() - inicioEstado)) / 1000 + 1;
    lcd.print("ATRAVESSE   ");
    lcd.print(restante < 10 ? " " : "");
    lcd.print(restante);
    lcd.print("s ");
  } else {
    lcd.print("ENCERRANDO! Pare");
  }

  lcd.setCursor(0, 1);
  char linha[17];
  if (estadoRampa == RAMPA_INVALIDA) {
    snprintf(linha, sizeof(linha), "Rampa: SENSOR?  ");
  } else {
    snprintf(linha, sizeof(linha), "%-9s %4dcm", nomeRampa(), (int)larguraMedia);
  }
  lcd.print(linha);
}

void imprimirSerial() {
  Serial.print("Semaforo: ");
  Serial.print(nomeSemaforo());
  Serial.print(" | leitura: ");
  Serial.print(ultimaLeituraBruta, 1);
  Serial.print(" cm");
  if (!leituraValida(ultimaLeituraBruta)) Serial.print(" (INVALIDA, descartada)");
  Serial.print(" | media: ");
  Serial.print(larguraMedia, 1);
  Serial.print(" cm | rampa: ");
  Serial.println(nomeRampa());
}

// =============================================================
void setup() {
  Serial.begin(115200);
  pinMode(PINO_TRIG, OUTPUT);
  pinMode(PINO_ECHO, INPUT);
  pinMode(PINO_LED_VERMELHO, OUTPUT);
  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_AMARELO, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);
  pinMode(PINO_BOTAO, INPUT_PULLUP);
  pinMode(PINO_TESTE_FALHA, INPUT);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(" AcessaBrasil   ");
  lcd.setCursor(0, 1);
  lcd.print("Semaforo sonoro ");
  delay(1500);  // única pausa bloqueante, só na inicialização
  lcd.clear();

  Serial.println("AcessaBrasil · semaforo sonoro iniciado");
  mudarEstado(AGUARDANDO);
}

void loop() {
  unsigned long agora = millis();

  if (agora - ultimaLeitura >= INTERVALO_LEITURA) {
    ultimaLeitura = agora;
    atualizarRampa();
  }

  atualizarSemaforo();
  atualizarLuzes();
  atualizarSom();

  if (agora - ultimoLcd >= INTERVALO_LCD) {
    ultimoLcd = agora;
    atualizarLcd();
  }
  if (agora - ultimoSerial >= INTERVALO_SERIAL) {
    ultimoSerial = agora;
    imprimirSerial();
  }
}

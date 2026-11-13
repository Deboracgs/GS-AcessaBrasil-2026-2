/* =============================================================
   AcessaBrasil · Interações em JavaScript
   Global Solution 2026.2 · Web Development
   Equipe: Débora Gonçalves da Silva (RM575926),
           Pedro Paulo Carvalho Coutinho (RM575957),
           Vanessa Santos Martins de Lima Nascimento (RM576450)
   ============================================================= */

/* ---------- 1. Constantes: as mesmas faixas do Python e do ESP32 ---------- */
const LIMITE_LIVRE = 120;    // cm, faixa livre mínima (ABNT NBR 9050)
const LIMITE_ATENCAO = 90;   // cm, abaixo disso a cadeira de rodas não passa
const LEITURA_MAXIMA = 400;  // cm, alcance do sensor HC-SR04

const AVISOS = {
  LIVRE: "Calçada livre: passagem acessível para cadeira de rodas.",
  "ATENÇÃO": "Passagem estreita: siga com cuidado ou use a rota alternativa.",
  BLOQUEADO: "Calçada bloqueada: use a rota alternativa indicada no mapa.",
  "INVÁLIDA": "Leitura descartada: digite um valor entre 1 e 400 cm."
};

const NOMES_RECURSOS = {
  cadeira: "Rampa ou elevador",
  visual: "Piso tátil ou braille",
  auditiva: "Atendimento em Libras",
  banheiro: "Banheiro acessível",
  sonoro: "Semáforo sonoro na travessia",
  autismo: "Ambiente amigável para autismo (TEA)",
  vaga_idoso: "Vaga para idoso",
  vaga_pcd: "Vaga PcD e TEA"
};

const RUIDO_CALMO = 55;     // dB, referência da OMS para áreas externas de dia
const RUIDO_MODERADO = 70;  // dB, acima disso é barulhento para quem tem sensibilidade sensorial

/* ---------- 2. Dados simulados dos locais (os mesmos do Python) ---------- */
const locais = [
  { nome: "Estação Carioca (metrô)", lat: -22.9068, lng: -43.1778, largura: 150, ruido: 78, recursos: ["cadeira", "visual", "sonoro"] },
  { nome: "Theatro Municipal", lat: -22.9090, lng: -43.1765, largura: 135, ruido: 62, recursos: ["cadeira", "visual", "banheiro", "sonoro"] },
  { nome: "Biblioteca Nacional", lat: -22.9097, lng: -43.1753, largura: 110, ruido: 45, recursos: ["cadeira", "banheiro", "autismo"] },
  { nome: "Museu Nacional de Belas Artes", lat: -22.9086, lng: -43.1758, largura: 95, ruido: 50, recursos: ["cadeira", "autismo"] },
  { nome: "Paço Imperial", lat: -22.9035, lng: -43.1739, largura: 160, ruido: 58, recursos: ["cadeira", "auditiva"] },
  { nome: "Estação das Barcas Praça XV", lat: -22.9030, lng: -43.1713, largura: 70, ruido: 82, recursos: ["cadeira", "visual", "sonoro"] },
  { nome: "CCBB Rio", lat: -22.9010, lng: -43.1765, largura: 140, ruido: 55, recursos: ["cadeira", "visual", "auditiva", "banheiro", "autismo"] },
  { nome: "Museu do Amanhã", lat: -22.8941, lng: -43.1795, largura: 210, ruido: 60, recursos: ["cadeira", "visual", "auditiva", "banheiro", "sonoro", "autismo"] },
  { nome: "Confeitaria Colombo", lat: -22.9050, lng: -43.1787, largura: 85, ruido: 72, recursos: [] },
  { nome: "Real Gabinete Português de Leitura", lat: -22.9055, lng: -43.1826, largura: 100, ruido: 40, recursos: ["autismo"] },
  { nome: "Parada VLT Cinelândia", lat: -22.9112, lng: -43.1762, largura: 125, ruido: 74, recursos: ["cadeira", "visual", "sonoro"] },
  { nome: "Praça Tiradentes", lat: -22.9068, lng: -43.1830, largura: 60, ruido: 68, recursos: ["cadeira"] },
  { nome: "Edifício Garagem Menezes Côrtes", lat: -22.9036, lng: -43.1772, largura: 130, ruido: 70, recursos: ["cadeira", "vaga_idoso", "vaga_pcd"] },
  { nome: "Passeio Público", lat: -22.9135, lng: -43.1758, largura: 180, ruido: 48, recursos: ["cadeira", "autismo", "vaga_idoso"] }
];

/* ---------- 3. Funções de decisão (mesma lógica do main.py) ---------- */
function classificarLargura(largura) {
  if (isNaN(largura) || largura <= 0 || largura > LEITURA_MAXIMA) {
    return "INVÁLIDA";
  } else if (largura >= LIMITE_LIVRE) {
    return "LIVRE";
  } else if (largura >= LIMITE_ATENCAO) {
    return "ATENÇÃO";
  } else {
    return "BLOQUEADO";
  }
}

function classificarRuido(decibeis) {
  if (decibeis <= RUIDO_CALMO) {
    return "Calmo";
  } else if (decibeis <= RUIDO_MODERADO) {
    return "Moderado";
  } else {
    return "Barulhento";
  }
}

function classificarLocal(recursos) {
  if (recursos.length === 0) {
    return { texto: "Sem acessibilidade", cor: "vermelho" };
  } else if (recursos.length <= 2) {
    return { texto: "Acessibilidade parcial", cor: "amarelo" };
  } else {
    return { texto: "Acessível", cor: "verde" };
  }
}

function corDoEstado(estado) {
  if (estado === "LIVRE") return "verde";
  if (estado === "ATENÇÃO") return "amarelo";
  if (estado === "BLOQUEADO") return "vermelho";
  return "cinza";
}

/* ---------- 4. Mapa com pins (Leaflet + OpenStreetMap) ---------- */
let mapa = null;
let camadaPins = null;
let filtroAtual = "todos";
let textoBusca = "";
let somenteCalmos = false;

function iniciarMapa() {
  const area = document.getElementById("mapaLeaflet");
  if (typeof L === "undefined") {
    // Sem internet a biblioteca não carrega: a lista continua funcionando
    area.innerHTML = "<p style='padding:20px'>Não foi possível carregar o mapa. Verifique a conexão. A lista ao lado continua funcionando.</p>";
    return;
  }
  mapa = L.map("mapaLeaflet").setView([-22.9045, -43.1775], 15);
  L.tileLayer("https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", {
    subdomains: "abc",
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors, style by HOT, hosted by OpenStreetMap France"
  }).addTo(mapa);
  camadaPins = L.layerGroup().addTo(mapa);
}

function criarPopup(local) {
  const tipo = classificarLocal(local.recursos);
  let recursosTexto = "Nenhum recurso informado";
  if (local.recursos.length > 0) {
    recursosTexto = local.recursos.map(function (r) { return NOMES_RECURSOS[r]; }).join(", ");
  }
  let calcada = "Sem leitura do sensor";
  if (local.largura) {
    const estado = classificarLargura(local.largura);
    calcada = "<span class='selo selo--" + corDoEstado(estado) + "'>" + estado + "</span> " +
              local.largura + " cm. " + AVISOS[estado];
  }
  let ruidoTexto = "Sem medição";
  if (local.ruido) {
    ruidoTexto = classificarRuido(local.ruido) + " (" + local.ruido + " dB)";
  }
  // Link para traçar a rota no Google Maps
  const rota = "https://www.google.com/maps/dir/?api=1&travelmode=walking&destination=" + local.lat + "," + local.lng;
  return "<div class='popup'>" +
    "<h4>" + local.nome + "</h4>" +
    "<p><span class='selo selo--" + tipo.cor + "'>" + tipo.texto + "</span></p>" +
    "<p><strong>Recursos:</strong> " + recursosTexto + "</p>" +
    "<p><strong>Calçada:</strong> " + calcada + "</p>" +
    "<p><strong>Ruído:</strong> " + ruidoTexto + "</p>" +
    "<p><a href='" + rota + "' target='_blank' rel='noopener'>Como chegar no Google Maps ↗</a></p>" +
    "</div>";
}

/* Um local aparece se combina com o filtro E com o texto da busca */
function localVisivel(local) {
  const passaFiltro = filtroAtual === "todos" || local.recursos.includes(filtroAtual);
  const passaBusca = local.nome.toLowerCase().includes(textoBusca);
  const passaRuido = !somenteCalmos || (local.ruido && classificarRuido(local.ruido) === "Calmo");
  return passaFiltro && passaBusca && passaRuido;
}

function desenharLocais() {
  const lista = document.getElementById("listaLocais");
  lista.innerHTML = "";
  if (camadaPins) camadaPins.clearLayers();

  let visiveis = 0;
  locais.forEach(function (local) {
    if (!localVisivel(local)) return;
    visiveis++;
    const tipo = classificarLocal(local.recursos);

    // Pin no mapa
    let marcador = null;
    if (mapa) {
      const icone = L.divIcon({
        className: "",
        html: "<div class='pin pin--" + tipo.cor + (local.novo ? " pin--novo" : "") + "'></div>",
        iconSize: [26, 26],
        iconAnchor: [13, 26],
        popupAnchor: [0, -24]
      });
      marcador = L.marker([local.lat, local.lng], { icon: icone, title: local.nome })
        .bindPopup(criarPopup(local))
        .addTo(camadaPins);
    }

    // Item na lista ao lado do mapa
    const item = document.createElement("li");
    const botao = document.createElement("button");
    botao.className = "item-local";
    botao.innerHTML = "<span class='ponto ponto--" + tipo.cor + "'></span>" +
      "<span>" + local.nome + "<small>" + tipo.texto +
      (local.ruido ? " · " + classificarRuido(local.ruido) : "") + "</small></span>";
    botao.addEventListener("click", function () {
      if (mapa && marcador) {
        mapa.setView([local.lat, local.lng], 17);
        marcador.openPopup();
      }
    });
    item.appendChild(botao);
    lista.appendChild(item);
  });

  const contador = document.getElementById("contador");
  if (visiveis === 0) {
    contador.textContent = "Nenhum local encontrado com esse filtro.";
  } else if (visiveis === 1) {
    contador.textContent = "1 local encontrado";
  } else {
    contador.textContent = visiveis + " locais encontrados";
  }
  atualizarIndicadores();
}

/* Indicadores de impacto da seção "Avaliar" */
function atualizarIndicadores() {
  let acessiveis = 0;
  let emAlerta = 0;
  let calmos = 0;
  locais.forEach(function (local) {
    if (local.recursos.length >= 3) acessiveis++;
    const estado = classificarLargura(local.largura);
    if (estado === "ATENÇÃO" || estado === "BLOQUEADO") emAlerta++;
    if (local.ruido && classificarRuido(local.ruido) === "Calmo") calmos++;
  });
  document.getElementById("totalCalmos").textContent = calmos;
  const percentual = Math.round((acessiveis / locais.length) * 100);
  document.getElementById("totalLocais").textContent = locais.length;
  document.getElementById("totalAcessiveis").textContent = percentual + "%";
  document.getElementById("totalAlerta").textContent = emAlerta;
}

/* ---------- 5. Filtros e busca ---------- */
document.querySelectorAll(".filtro").forEach(function (botao) {
  botao.addEventListener("click", function () {
    document.querySelectorAll(".filtro").forEach(function (b) { b.classList.remove("ativo"); });
    botao.classList.add("ativo");
    filtroAtual = botao.dataset.recurso;
    desenharLocais();
  });
});

document.getElementById("somenteCalmos").addEventListener("change", function (evento) {
  somenteCalmos = evento.target.checked;
  desenharLocais();
});

document.getElementById("busca").addEventListener("input", function (evento) {
  textoBusca = evento.target.value.trim().toLowerCase();
  desenharLocais();
});

/* ---------- 6. Simulador da calçada ---------- */
document.getElementById("formSimulador").addEventListener("submit", function (evento) {
  evento.preventDefault();
  const campo = document.getElementById("largura");
  const largura = Number(campo.value);
  const estado = classificarLargura(campo.value === "" ? NaN : largura);
  const caixa = document.getElementById("resultadoSimulador");

  caixa.classList.remove("livre", "atencao", "bloqueado");
  if (estado === "LIVRE") caixa.classList.add("livre");
  else if (estado === "ATENÇÃO") caixa.classList.add("atencao");
  else if (estado === "BLOQUEADO") caixa.classList.add("bloqueado");

  caixa.innerHTML = "<span class='simulador__estado'>" + estado + "</span><p>" + AVISOS[estado] + "</p>";
});

/* ---------- 7. Formulário de avaliação: cria um novo pin ---------- */
document.getElementById("formAvaliar").addEventListener("submit", function (evento) {
  evento.preventDefault();
  const campoNome = document.getElementById("nomeLocal");
  const campoLargura = document.getElementById("larguraLocal");
  const mensagem = document.getElementById("mensagemForm");
  const nome = campoNome.value.trim();

  campoNome.classList.remove("campo-erro");
  campoLargura.classList.remove("campo-erro");
  mensagem.className = "mensagem";

  // Validações simples
  if (nome.length < 3) {
    campoNome.classList.add("campo-erro");
    mensagem.classList.add("erro");
    mensagem.textContent = "Digite o nome do local (pelo menos 3 letras).";
    return;
  }
  let largura = null;
  if (campoLargura.value !== "") {
    largura = Number(campoLargura.value);
    if (classificarLargura(largura) === "INVÁLIDA") {
      campoLargura.classList.add("campo-erro");
      mensagem.classList.add("erro");
      mensagem.textContent = "A largura precisa estar entre 1 e 400 cm.";
      return;
    }
  }

  const recursos = [];
  document.querySelectorAll("input[name='recurso']:checked").forEach(function (caixa) {
    recursos.push(caixa.value);
  });

  // O novo pin aparece perto do centro atual do mapa
  let lat = -22.9045, lng = -43.1775;
  if (mapa) {
    const centro = mapa.getCenter();
    lat = centro.lat + (Math.random() - 0.5) * 0.002;
    lng = centro.lng + (Math.random() - 0.5) * 0.002;
  }

  // Ruído informado pela pessoa vira um valor aproximado em dB
  const barulho = document.getElementById("ruidoLocal").value;
  let ruido = null;
  if (barulho === "calmo") ruido = 50;
  else if (barulho === "moderado") ruido = 65;
  else if (barulho === "barulhento") ruido = 80;

  locais.push({ nome: nome, lat: lat, lng: lng, largura: largura, ruido: ruido, recursos: recursos, novo: true });

  // Volta os filtros para "Todos" para o pin novo aparecer
  filtroAtual = "todos";
  textoBusca = "";
  somenteCalmos = false;
  document.getElementById("busca").value = "";
  document.getElementById("somenteCalmos").checked = false;
  document.querySelectorAll(".filtro").forEach(function (b) {
    b.classList.toggle("ativo", b.dataset.recurso === "todos");
  });
  desenharLocais();

  const tipo = classificarLocal(recursos);
  mensagem.classList.add("sucesso");
  mensagem.textContent = "Obrigado! " + nome + " entrou no mapa como \"" + tipo.texto + "\".";
  evento.target.reset();
});

/* ---------- 7b. Semáforo sonoro de pedestres ----------
   Estados (os mesmos do ESP32):
   AGUARDE    -> vermelho, tom localizador lento (1 bipe a cada 1,5 s)
   ATRAVESSE  -> verde, bipes rápidos (a cada 0,3 s) por 8 segundos
   ENCERRANDO -> verde piscando, bipes muito rápidos (a cada 0,15 s) por 4 segundos */
const TEMPO_VERDE = 8000;
const TEMPO_ENCERRANDO = 4000;
let audio = null;
let intervaloBipe = null;
let travessiaEmAndamento = false;

function tocarBipe(frequencia) {
  if (!document.getElementById("somLigado").checked) return;
  try {
    if (audio === null) audio = new (window.AudioContext || window.webkitAudioContext)();
    const oscilador = audio.createOscillator();
    const volume = audio.createGain();
    oscilador.frequency.value = frequencia;
    volume.gain.value = 0.15;
    oscilador.connect(volume);
    volume.connect(audio.destination);
    oscilador.start();
    oscilador.stop(audio.currentTime + 0.08);
  } catch (erro) {
    // navegador sem suporte a áudio: o semáforo continua funcionando só com as luzes
  }
}

function bipar(intervalo, frequencia) {
  clearInterval(intervaloBipe);
  tocarBipe(frequencia);
  intervaloBipe = setInterval(function () { tocarBipe(frequencia); }, intervalo);
}

function mudarSemaforo(estado) {
  const vermelha = document.getElementById("luzVermelha");
  const verde = document.getElementById("luzVerde");
  const texto = document.getElementById("estadoSemaforo");
  vermelha.classList.remove("acesa");
  verde.classList.remove("acesa", "piscando");

  if (estado === "ATRAVESSE") {
    verde.classList.add("acesa");
    texto.textContent = "ATRAVESSE · sinal aberto para pedestres";
    bipar(300, 880);
  } else if (estado === "ENCERRANDO") {
    verde.classList.add("acesa", "piscando");
    texto.textContent = "ENCERRANDO · não comece a travessia agora";
    bipar(150, 880);
  } else {
    vermelha.classList.add("acesa");
    texto.textContent = "AGUARDE · sinal fechado para pedestres";
    if (travessiaEmAndamento) bipar(1500, 440);   // tom localizador
  }
}

document.getElementById("botaoTravessia").addEventListener("click", function () {
  const botao = this;
  botao.disabled = true;
  travessiaEmAndamento = true;
  document.getElementById("estadoSemaforo").textContent = "PEDIDO REGISTRADO · aguarde o sinal abrir";
  bipar(1500, 440);
  setTimeout(function () {
    mudarSemaforo("ATRAVESSE");
    setTimeout(function () {
      mudarSemaforo("ENCERRANDO");
      setTimeout(function () {
        travessiaEmAndamento = false;
        clearInterval(intervaloBipe);
        mudarSemaforo("AGUARDE");
        botao.disabled = false;
      }, TEMPO_ENCERRANDO);
    }, TEMPO_VERDE);
  }, 2000);
});

/* ---------- 8. Modo claro / escuro ---------- */
function aplicarTema(escuro) {
  document.body.classList.toggle("escuro", escuro);
  document.getElementById("iconeTema").textContent = escuro ? "☀" : "☾";
  document.getElementById("botaoTema").setAttribute("aria-pressed", escuro ? "true" : "false");
}

function lerPreferencia(chave) {
  try { return localStorage.getItem(chave); } catch (erro) { return null; }
}
function salvarPreferencia(chave, valor) {
  try { localStorage.setItem(chave, valor); } catch (erro) { /* navegador sem armazenamento */ }
}

document.getElementById("botaoTema").addEventListener("click", function () {
  const ficaEscuro = !document.body.classList.contains("escuro");
  aplicarTema(ficaEscuro);
  salvarPreferencia("acessabrasil-tema", ficaEscuro ? "escuro" : "claro");
});

/* ---------- 9. Tamanho da fonte (acessibilidade) ---------- */
let tamanhoFonte = 100;
function aplicarFonte() {
  document.documentElement.style.setProperty("--fonte-base", tamanhoFonte + "%");
  salvarPreferencia("acessabrasil-fonte", String(tamanhoFonte));
}
document.getElementById("aumentarFonte").addEventListener("click", function () {
  if (tamanhoFonte < 150) { tamanhoFonte += 10; aplicarFonte(); }
});
document.getElementById("diminuirFonte").addEventListener("click", function () {
  if (tamanhoFonte > 80) { tamanhoFonte -= 10; aplicarFonte(); }
});

/* ---------- 10. Menu mobile ---------- */
const menuBotao = document.getElementById("menuBotao");
const menu = document.getElementById("menu");
menuBotao.addEventListener("click", function () {
  const aberto = menu.classList.toggle("aberto");
  menuBotao.setAttribute("aria-expanded", aberto ? "true" : "false");
});
menu.querySelectorAll("a").forEach(function (link) {
  link.addEventListener("click", function () {
    menu.classList.remove("aberto");
    menuBotao.setAttribute("aria-expanded", "false");
  });
});

/* ---------- Inicialização ---------- */
(function iniciar() {
  // Tema: usa o salvo; se não houver, segue o sistema do usuário
  const temaSalvo = lerPreferencia("acessabrasil-tema");
  const sistemaEscuro = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  aplicarTema(temaSalvo ? temaSalvo === "escuro" : sistemaEscuro);

  const fonteSalva = Number(lerPreferencia("acessabrasil-fonte"));
  if (fonteSalva >= 80 && fonteSalva <= 150) { tamanhoFonte = fonteSalva; aplicarFonte(); }

  iniciarMapa();
  desenharLocais();
})();

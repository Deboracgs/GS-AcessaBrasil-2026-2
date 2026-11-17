# =============================================================
# AcessaBrasil · Modelagem Matemática do Semáforo Sonoro Acessível
# Global Solution 2026.2 · Differentiated Problem Solving
# FIAP Rio de Janeiro · Engenharia de Software 1º ano
#
# Equipe:
#   Débora Gonçalves da Silva                  RM575926
#   Pedro Paulo Carvalho Coutinho              RM575957
#   Vanessa Santos Martins de Lima Nascimento  RM576450
#
# Problema: pessoas cegas e idosas precisam atravessar a rua com segurança.
# O semáforo sonoro do AcessaBrasil precisa (1) ser ouvido sem incomodar
# a vizinhança e (2) dar tempo suficiente para quem anda devagar.
#
# Modelo 1 · função LOGARÍTMICA (ISO 9613-2, divergência geométrica)
#     L(d) = L1 - 20·log10(d)
# Modelo 2 · função POLINOMIAL de 1º grau (Manual Brasileiro de
#            Sinalização de Trânsito, Vol. V: tempo = extensão / velocidade)
#     T(x) = x / v
#
# Dados reais usados:
#   - Ruído (LAeq, dB) medido em 10 pontos de Irajá, Rio de Janeiro, em
#     20/05/2023 e 01/06/2023 (Pereira e Torres, SINGEURB 2023, UFRJ).
#   - Velocidade de marcha de 1.191 idosos de São Paulo: média de 2,7 km/h
#     (Duim, Lebrão e Antunes, Journal of Transport & Health, 2017).
#   - Regras do semáforo sonoro (MUTCD, FHWA, EUA): som audível de 6 a 12 pés
#     do botão, volume máximo de 100 dBA, ajuste automático ao ruído ambiente.
#
# Como rodar:  pip install numpy matplotlib   e depois   python modelagem.py
# =============================================================

import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_GRAFICOS = os.path.join(PASTA, "graficos")
os.makedirs(PASTA_GRAFICOS, exist_ok=True)

# ---------------- Dados reais ----------------
# LAeq (dB) por ponto: (sábado 20/05/2023, quinta 01/06/2023)
RUIDO_IRAJA = {
    "A": (65, 68), "B": (67, 76), "C": (75, 75), "D": (75, 64), "E": (55, 60),
    "F": (60, 75), "G": (75, 76), "H": (73, 64), "I": (61, 61), "J": (63, 69),
}
LIMITE_OMS = 55.0        # dB, exposição diurna em área externa (OMS, 1999)
LIMITE_NBR = 60.0        # dB, área mista diurna (NBR 10151:2019, citada no estudo)

# ---------------- Parâmetros das fontes ----------------
PE_PARA_M = 0.3048
DIST_AUDIVEL_MIN = 6 * PE_PARA_M    # 1,83 m (MUTCD)
DIST_AUDIVEL_MAX = 12 * PE_PARA_M   # 3,66 m (MUTCD)
FOLGA = 2.0              # dB acima do ambiente no limite de audibilidade (faixa de 2 a 5 dBA do PROWAG)
VOLUME_MAXIMO = 100.0    # dBA (MUTCD)

VEL_MANUAL = 1.2         # m/s, Manual Brasileiro de Sinalização de Trânsito / CET-SP
VEL_IDOSO_P15 = 0.9      # m/s, 15º percentil de idosos (Knoblauch et al.; U.S. Access Board)
VEL_IDOSO_MEDIA = 2.7 / 3.6   # m/s, média de idosos de São Paulo (Duim et al., 2017) = 0,75 m/s
TEMPO_FIRMWARE = 15.0    # s, verde + verde piscando no ESP32 do AcessaBrasil

# ---------------- Estilo dos gráficos ----------------
VERDE, LARANJA, AZUL = "#0b7a5a", "#c86a00", "#1f5fbf"
TINTA, SUAVE, GRADE = "#1b2a24", "#5b6b64", "#dfe7e3"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": GRADE, "axes.labelcolor": TINTA,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": TINTA,
    "xtick.color": SUAVE, "ytick.color": SUAVE,
    "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 150,
})

saida = []


def registrar(texto=""):
    print(texto)
    saida.append(texto)


def br(numero, casas=1):
    """Formata número com vírgula decimal."""
    return f"{numero:.{casas}f}".replace(".", ",")


# =============================================================
# PARTE 0 · Diagnóstico com dados reais de ruído
# =============================================================
def diagnostico_ruido():
    registrar("=== Diagnóstico: ruído medido em Irajá (Rio de Janeiro) ===")
    valores = np.array([v for par in RUIDO_IRAJA.values() for v in par], dtype=float)
    registrar(f"Medições: {len(valores)} (10 pontos x 2 dias)")
    registrar(f"Média: {br(valores.mean())} dB · mínimo: {br(valores.min(), 0)} dB · máximo: {br(valores.max(), 0)} dB")
    acima_oms = np.mean(valores > LIMITE_OMS) * 100
    acima_nbr = np.mean(valores > LIMITE_NBR) * 100
    registrar(f"Acima de {br(LIMITE_OMS, 0)} dB (OMS): {br(acima_oms, 0)}% · "
              f"acima de {br(LIMITE_NBR, 0)} dB (NBR 10151): {br(acima_nbr, 0)}%")
    registrar()
    return valores


# =============================================================
# MODELO 1 · LOGARÍTMICO: nível do bipe em função da distância
#   L(d) = L1 - 20·log10(d)        (d em metros, L1 = nível a 1 m)
# =============================================================
def nivel(d, l1):
    """Nível sonoro (dB) a d metros de um alto-falante com nível L1 a 1 m."""
    return l1 - 20 * np.log10(d)


def distancia_para_nivel(l_alvo, l1):
    """Função inversa (exponencial): distância em que o nível cai para l_alvo."""
    return 10 ** ((l1 - l_alvo) / 20)


def volume_necessario(ruido_ambiente):
    """L1 para que o bipe chegue a 3,66 m com 2 dB acima do ambiente, limitado a 100 dBA."""
    return min(VOLUME_MAXIMO, ruido_ambiente + FOLGA + 20 * math.log10(DIST_AUDIVEL_MAX))


def modelo_logaritmico():
    registrar("=== Modelo 1 · Logarítmico: L(d) = L1 - 20·log10(d) ===")
    registrar(f"Queda a cada vez que a distância dobra: {br(20 * math.log10(2), 2)} dB")
    registrar("Derivada: L'(d) = -20/(d·ln10) < 0 -> função decrescente em todo o domínio")
    acrescimo = FOLGA + 20 * math.log10(DIST_AUDIVEL_MAX)
    registrar(f"Volume a 1 m necessário: L1 = ruído ambiente + {br(acrescimo)} dB (máximo 100 dBA)")
    alcance = distancia_para_nivel(0, acrescimo)  # distância em que o bipe iguala o ambiente
    registrar(f"Distância em que o bipe se iguala ao ruído ambiente: {br(alcance, 2)} m")
    registrar()
    registrar("Simulação com o ruído real de cada ponto (média dos dois dias):")
    registrar("Ponto | ruído ambiente | volume a 1 m | nível a 1,83 m | nível a 3,66 m")
    tabela = []
    for ponto, (sab, qui) in RUIDO_IRAJA.items():
        ambiente = (sab + qui) / 2
        l1 = volume_necessario(ambiente)
        tabela.append((ponto, ambiente, l1, nivel(DIST_AUDIVEL_MIN, l1), nivel(DIST_AUDIVEL_MAX, l1)))
        registrar(f"  {ponto}   | {br(ambiente)} dB | {br(l1)} dB | "
                  f"{br(nivel(DIST_AUDIVEL_MIN, l1))} dB | {br(nivel(DIST_AUDIVEL_MAX, l1))} dB")
    # Comparação: volume fixo (o maior necessário) aplicado no ponto mais calmo
    volume_fixo = max(t[2] for t in tabela)
    ambiente_calmo = min(t[1] for t in tabela)
    alcance_fixo = distancia_para_nivel(ambiente_calmo, volume_fixo)
    registrar(f"Se o volume fosse fixo em {br(volume_fixo)} dB, no ponto mais calmo ({br(ambiente_calmo)} dB) "
              f"o bipe só se igualaria ao ambiente a {br(alcance_fixo)} m (contra {br(alcance, 2)} m com ajuste)")
    registrar()

    # Gráfico 1: L(d) para o ponto mais calmo e o mais barulhento
    fig, ax = plt.subplots(figsize=(8, 4.4))
    d = np.linspace(0.5, 10, 400)
    for ambiente, cor, nome in [(57.5, VERDE, "ponto E (57,5 dB)"), (75.5, LARANJA, "ponto G (75,5 dB)")]:
        l1 = volume_necessario(ambiente)
        ax.plot(d, nivel(d, l1), color=cor, lw=2, label=f"bipe ajustado ao {nome}")
        ax.axhline(ambiente, color=cor, lw=1, ls="--")
    ax.axvspan(DIST_AUDIVEL_MIN, DIST_AUDIVEL_MAX, color=AZUL, alpha=0.08, lw=0)
    ax.text((DIST_AUDIVEL_MIN + DIST_AUDIVEL_MAX) / 2, 99, "zona de\naudibilidade\n(1,83 a 3,66 m)",
            ha="center", va="top", fontsize=9, color=TINTA)
    ax.text(9.9, 57.5 + 0.8, "ruído ambiente E", ha="right", fontsize=9, color=TINTA)
    ax.text(9.9, 75.5 + 0.8, "ruído ambiente G", ha="right", fontsize=9, color=TINTA)
    ax.set_xlim(0.5, 10)
    ax.set_ylim(50, 100)
    ax.set_xlabel("distância do botão do semáforo, d (m)")
    ax.set_ylabel("nível sonoro do bipe, L(d) (dB)")
    ax.set_title("Modelo 1: L(d) = L1 − 20·log10(d)")
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_GRAFICOS, "1-modelo-logaritmico.png"))
    plt.close(fig)

    # Gráfico 2: volume necessário por ponto real
    fig, ax = plt.subplots(figsize=(8, 4.4))
    pontos = [t[0] for t in tabela]
    ambientes = [t[1] for t in tabela]
    volumes = [t[2] for t in tabela]
    x = np.arange(len(pontos))
    ax.bar(x - 0.2, ambientes, width=0.38, color=VERDE, label="ruído ambiente medido (média)")
    ax.bar(x + 0.2, volumes, width=0.38, color=LARANJA, label="volume do bipe a 1 m (modelo)")
    ax.axhline(VOLUME_MAXIMO, color=SUAVE, lw=1, ls="--")
    ax.text(len(pontos) - 0.5, VOLUME_MAXIMO + 1.5, "limite de 100 dBA (MUTCD)", ha="right", fontsize=9, color=SUAVE)
    ax.set_xticks(x)
    ax.set_xticklabels(pontos)
    ax.set_ylim(0, 115)
    ax.set_xlabel("ponto de medição em Irajá")
    ax.set_ylabel("nível (dB)")
    ax.set_title("Volume adaptativo do semáforo com o ruído real")
    ax.legend(loc="upper left", fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_GRAFICOS, "2-volume-por-ponto.png"))
    plt.close(fig)
    return tabela, alcance, acrescimo


# =============================================================
# MODELO 2 · POLINOMIAL (1º grau): tempo de travessia
#   T(x) = x / v
# =============================================================
def tempo(x, v):
    """Tempo (s) para atravessar x metros a v m/s."""
    return x / v


def modelo_polinomial():
    registrar("=== Modelo 2 · Polinomial: T(x) = x / v ===")
    perfis = [(VEL_MANUAL, "padrão do Manual (1,2 m/s)"),
              (VEL_IDOSO_P15, "idoso, 15º percentil (0,9 m/s)"),
              (VEL_IDOSO_MEDIA, "idoso, média em SP (0,75 m/s)")]
    for v, nome in perfis:
        registrar(f"  {nome}: coeficiente angular 1/v = {br(1 / v, 2)} s/m · "
                  f"com {br(TEMPO_FIRMWARE, 0)} s atravessa até {br(v * TEMPO_FIRMWARE)} m")
    extra = 1 / VEL_IDOSO_MEDIA - 1 / VEL_MANUAL
    registrar(f"Tempo extra para o idoso médio: ΔT(x) = {br(extra, 2)}·x segundos")
    registrar("Largura | 1,2 m/s | 0,9 m/s | 0,75 m/s | tempo extra (0,75 vs 1,2)")
    tabela = []
    for largura in [6, 8, 10, 12, 15, 20]:
        linha = [largura] + [tempo(largura, v) for v, _ in perfis] + [extra * largura]
        tabela.append(linha)
        registrar(f"  {largura:2d} m  | {br(linha[1])} s | {br(linha[2])} s | {br(linha[3])} s | +{br(linha[4])} s")
    registrar()

    fig, ax = plt.subplots(figsize=(8, 4.4))
    x = np.linspace(0, 25, 200)
    for (v, nome), cor in zip(perfis, [VERDE, AZUL, LARANJA]):
        ax.plot(x, tempo(x, v), color=cor, lw=2, label=nome)
    ax.axhline(TEMPO_FIRMWARE, color=SUAVE, lw=1, ls="--")
    ax.text(0.3, TEMPO_FIRMWARE + 0.6, "semáforo atual: 15 s",
            ha="left", fontsize=9, color=SUAVE)
    for v, cor in [(VEL_MANUAL, VERDE), (VEL_IDOSO_MEDIA, LARANJA)]:
        xm = v * TEMPO_FIRMWARE
        ax.scatter([xm], [TEMPO_FIRMWARE], s=55, color=cor, edgecolor="white", linewidth=1.5, zorder=3)
        ax.annotate(f"{br(xm)} m", (xm, TEMPO_FIRMWARE), xytext=(xm - 0.5, TEMPO_FIRMWARE + 5),
                    ha="right", fontsize=9, color=TINTA,
                    arrowprops=dict(arrowstyle="-", color=SUAVE, lw=0.8))
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 35)
    ax.set_xlabel("largura da travessia, x (m)")
    ax.set_ylabel("tempo necessário, T(x) (s)")
    ax.set_title("Modelo 2: T(x) = x / v para três velocidades")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_GRAFICOS, "3-modelo-travessia.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.4))
    larg = np.arange(4, 26, 2)
    ax.bar(larg, extra * larg, width=1.4, color=LARANJA)
    for xi in [10, 20]:
        ax.text(xi, extra * xi + 0.3, f"+{br(extra * xi)} s", ha="center", fontsize=9, color=TINTA)
    ax.set_xlabel("largura da travessia, x (m)")
    ax.set_ylabel("tempo extra, ΔT(x) (s)")
    ax.set_title("Tempo extra que o idoso médio precisa: ΔT(x) = 0,5·x")
    ax.set_ylim(0, 14)
    fig.tight_layout()
    fig.savefig(os.path.join(PASTA_GRAFICOS, "4-tempo-extra.png"))
    plt.close(fig)
    return tabela


if __name__ == "__main__":
    diagnostico_ruido()
    modelo_logaritmico()
    modelo_polinomial()
    with open(os.path.join(PASTA, "resultados.txt"), "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(saida) + "\n")
    print("Gráficos salvos em", PASTA_GRAFICOS)

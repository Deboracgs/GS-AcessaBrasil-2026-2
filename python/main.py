# =============================================================
# AcessaBrasil · O Cérebro da CitizenTech
# Global Solution 2026.2 · Computational Thinking with Python
# FIAP Rio de Janeiro · Engenharia de Software 1º ano
#
# Equipe:
#   Débora Gonçalves da Silva                  RM575926
#   Pedro Paulo Carvalho Coutinho              RM575957
#   Vanessa Santos Martins de Lima Nascimento  RM576450
#
# O que o programa faz:
#   Recebe leituras simuladas dos sensores instalados junto aos
#   semáforos sonoros de pedestres em frente a locais do Centro do Rio:
#   a largura livre da calçada (cm) e o nível de ruído (dB).
#   Classifica cada leitura em faixas, calcula o resumo e decide qual
#   aviso o cidadão vai ver na página do AcessaBrasil. Atende pessoas
#   com deficiência, pessoas autistas (TEA) e idosos.
#
# Todos os dados abaixo são SIMULADOS para o protótipo.
# =============================================================

# ---------- Constantes (as mesmas faixas do ESP32 e do JavaScript) ----------
LIMITE_LIVRE = 120     # cm: faixa livre mínima de calçada (ABNT NBR 9050)
LIMITE_ATENCAO = 90    # cm: abaixo disso uma cadeira de rodas não passa
LEITURA_MAXIMA = 400   # cm: alcance máximo do sensor ultrassônico HC-SR04
RUIDO_CALMO = 55       # dB: até aqui o ambiente é calmo (referência da OMS para áreas externas de dia)
RUIDO_MODERADO = 70    # dB: acima disso o ambiente é barulhento para quem tem sensibilidade sensorial

# Mensagens: são os mesmos textos que aparecem na página
AVISOS = {
    "LIVRE": "Calçada livre: passagem acessível para cadeira de rodas.",
    "ATENÇÃO": "Passagem estreita: siga com cuidado ou use a rota alternativa.",
    "BLOQUEADO": "Calçada bloqueada: use a rota alternativa indicada no mapa.",
    "INVÁLIDA": "Leitura descartada: o sensor vai medir de novo.",
}

# Recursos de acessibilidade usados nos filtros do mapa
RECURSOS = {
    "1": ("cadeira", "Cadeira de rodas (rampa ou elevador)"),
    "2": ("visual", "Deficiência visual (piso tátil, braille, audiodescrição)"),
    "3": ("auditiva", "Deficiência auditiva (atendimento em Libras)"),
    "4": ("banheiro", "Banheiro acessível"),
    "5": ("sonoro", "Semáforo sonoro na travessia mais próxima"),
    "6": ("autismo", "Ambiente amigável para autismo (TEA): calmo, com sala ou horário silencioso"),
    "7": ("vaga_idoso", "Vaga de estacionamento para idoso"),
    "8": ("vaga_pcd", "Vaga de estacionamento PcD e TEA"),
}

# ---------- Lista de registros simulados (14 leituras) ----------
# Cada registro é um dicionário: local, horário da leitura,
# largura livre medida (cm), ruído medido (dB) e recursos do local.
leituras = [
    {"local": "Estação Carioca (metrô)", "hora": "07:30", "largura": 150, "ruido": 78, "recursos": ["cadeira", "visual", "sonoro"]},
    {"local": "Theatro Municipal", "hora": "08:00", "largura": 135, "ruido": 62, "recursos": ["cadeira", "visual", "banheiro", "sonoro"]},
    {"local": "Biblioteca Nacional", "hora": "08:30", "largura": 110, "ruido": 45, "recursos": ["cadeira", "banheiro", "autismo"]},
    {"local": "Museu Nacional de Belas Artes", "hora": "09:00", "largura": 95, "ruido": 50, "recursos": ["cadeira", "autismo"]},
    {"local": "Paço Imperial", "hora": "09:30", "largura": 160, "ruido": 58, "recursos": ["cadeira", "auditiva"]},
    {"local": "Estação das Barcas Praça XV", "hora": "10:00", "largura": 70, "ruido": 82, "recursos": ["cadeira", "visual", "sonoro"]},
    {"local": "CCBB Rio", "hora": "10:30", "largura": 140, "ruido": 55, "recursos": ["cadeira", "visual", "auditiva", "banheiro", "autismo"]},
    {"local": "Museu do Amanhã", "hora": "11:00", "largura": 210, "ruido": 60, "recursos": ["cadeira", "visual", "auditiva", "banheiro", "sonoro", "autismo"]},
    {"local": "Confeitaria Colombo", "hora": "11:30", "largura": 85, "ruido": 72, "recursos": []},
    {"local": "Real Gabinete Português de Leitura", "hora": "12:00", "largura": 100, "ruido": 40, "recursos": ["autismo"]},
    {"local": "Parada VLT Cinelândia", "hora": "12:30", "largura": 125, "ruido": 74, "recursos": ["cadeira", "visual", "sonoro"]},
    {"local": "Praça Tiradentes", "hora": "13:00", "largura": 60, "ruido": 68, "recursos": ["cadeira"]},
    {"local": "Edifício Garagem Menezes Côrtes", "hora": "13:30", "largura": 130, "ruido": 70, "recursos": ["cadeira", "vaga_idoso", "vaga_pcd"]},
    {"local": "Passeio Público", "hora": "14:00", "largura": 180, "ruido": 48, "recursos": ["cadeira", "autismo", "vaga_idoso"]},
]


# ---------- Funções de decisão ----------
def classificar_largura(largura):
    """Recebe a largura livre em cm e devolve o estado da calçada."""
    if largura <= 0 or largura > LEITURA_MAXIMA:
        return "INVÁLIDA"
    elif largura >= LIMITE_LIVRE:
        return "LIVRE"
    elif largura >= LIMITE_ATENCAO:
        return "ATENÇÃO"
    else:
        return "BLOQUEADO"


def classificar_ruido(decibeis):
    """Classifica o ruído do local, pensando em quem tem sensibilidade sensorial."""
    if decibeis <= RUIDO_CALMO:
        return "Calmo"
    elif decibeis <= RUIDO_MODERADO:
        return "Moderado"
    else:
        return "Barulhento"


def classificar_local(recursos):
    """Classifica o pin do mapa pela quantidade de recursos do local."""
    quantidade = len(recursos)
    if quantidade == 0:
        return "Sem acessibilidade"
    elif quantidade <= 2:
        return "Acessibilidade parcial"
    else:
        return "Acessível"


def ler_opcao(mensagem):
    """Lê um texto do teclado sem deixar o programa quebrar."""
    try:
        return input(mensagem).strip()
    except (EOFError, KeyboardInterrupt):
        return "0"   # se o usuário fechar a entrada, saímos com segurança


def ler_numero(mensagem):
    """Pede um número inteiro até o usuário digitar um valor válido."""
    while True:
        texto = ler_opcao(mensagem)
        try:
            return int(texto)
        except ValueError:
            print("  Entrada inválida. Digite apenas números inteiros, por exemplo 120.")


# ---------- Opções do menu ----------
def mostrar_leituras():
    print("\n--- Leituras dos sensores (calçada e ruído) ---")
    for registro in leituras:
        estado = classificar_largura(registro["largura"])
        tipo = classificar_local(registro["recursos"])
        ruido = classificar_ruido(registro["ruido"])
        print(f"{registro['hora']}  {registro['local']:<34} {registro['largura']:>4} cm  "
              f"{estado:<10} | {registro['ruido']} dB {ruido:<10} | {tipo}")


def mostrar_resumo():
    validas = []          # leituras que o sensor considera confiáveis
    em_alerta = 0         # ATENÇÃO + BLOQUEADO
    bloqueadas = 0
    for registro in leituras:
        estado = classificar_largura(registro["largura"])
        if estado != "INVÁLIDA":
            validas.append(registro["largura"])
            if estado == "ATENÇÃO" or estado == "BLOQUEADO":
                em_alerta += 1
            if estado == "BLOQUEADO":
                bloqueadas += 1

    if len(validas) == 0:
        print("\nNenhuma leitura válida para resumir.")
        return

    media = sum(validas) / len(validas)
    maior = max(validas)
    percentual = em_alerta / len(validas) * 100

    print("\n--- Resumo do dia · Centro do Rio ---")
    print(f"Leituras válidas: {len(validas)} de {len(leituras)}")
    print(f"Largura livre média: {media:.1f} cm")
    print(f"Maior largura livre: {maior} cm")
    print(f"Leituras em alerta (ATENÇÃO ou BLOQUEADO): {em_alerta} de {len(validas)} ({percentual:.1f}%)")

    # Ruído: média e locais calmos (importante para pessoas autistas)
    soma_ruido = 0
    calmos = 0
    for registro in leituras:
        soma_ruido += registro["ruido"]
        if classificar_ruido(registro["ruido"]) == "Calmo":
            calmos += 1
    print(f"Ruído médio: {soma_ruido / len(leituras):.1f} dB · locais calmos: {calmos} de {len(leituras)}")

    # Decisão do aviso geral que vai para a página
    if bloqueadas >= 3:
        print("AVISO: várias calçadas bloqueadas hoje. Consulte a rota alternativa antes de sair.")
    elif em_alerta > 0:
        print("AVISO: há trechos estreitos no Centro. Confira o mapa antes de sair.")
    else:
        print("AVISO: calçadas monitoradas livres. Bom trajeto!")


def buscar_por_recurso():
    print("\nQual recurso você precisa?")
    for chave, (_, descricao) in RECURSOS.items():
        print(f"  {chave} - {descricao}")
    escolha = ler_opcao("> ")
    if escolha not in RECURSOS:
        print("  Opção inválida. Escolha um número de 1 a 8.")
        return
    recurso, descricao = RECURSOS[escolha]
    print(f"\nLocais com: {descricao}")
    encontrados = 0
    for registro in leituras:
        if recurso in registro["recursos"]:
            estado = classificar_largura(registro["largura"])
            ruido = classificar_ruido(registro["ruido"])
            print(f"  {registro['local']:<34} calçada: {estado:<10} ruído: {ruido}")
            encontrados += 1
    if encontrados == 0:
        print("  Nenhum local encontrado com esse recurso.")


def registrar_leitura():
    print("\nNova leitura do sensor")
    local = ler_opcao("Nome do local: ")
    if local == "":
        print("  O nome do local não pode ficar vazio.")
        return
    largura = ler_numero("Largura livre medida (cm): ")
    estado = classificar_largura(largura)
    if estado == "INVÁLIDA":
        print(f"  {largura} cm está fora do alcance do sensor. {AVISOS['INVÁLIDA']}")
        return
    ruido = ler_numero("Ruído medido (dB): ")
    if ruido <= 0 or ruido > 140:
        print("  Ruído fora da faixa do sensor (1 a 140 dB). Leitura descartada.")
        return
    leituras.append({"local": local, "hora": "agora", "largura": largura, "ruido": ruido, "recursos": []})
    print(f"  Leitura registrada: {estado}, ambiente {classificar_ruido(ruido).lower()}. {AVISOS[estado]}")


def verificar_calcada():
    print("\nSimulador: quanto mede a passagem livre?")
    largura = ler_numero("Largura livre (cm): ")
    estado = classificar_largura(largura)
    print(f"  Estado: {estado}")
    print(f"  {AVISOS[estado]}")


# ---------- Programa principal: menu em loop ----------
def main():
    while True:
        print("\n=== AcessaBrasil · Calçadas do Centro ===")
        print("1 - Ver leituras classificadas")
        print("2 - Resumo do dia")
        print("3 - Buscar locais por recurso de acessibilidade")
        print("4 - Registrar nova leitura")
        print("5 - Verificar uma calçada")
        print("0 - Sair")
        opcao = ler_opcao("> ")

        if opcao == "1":
            mostrar_leituras()
        elif opcao == "2":
            mostrar_resumo()
        elif opcao == "3":
            buscar_por_recurso()
        elif opcao == "4":
            registrar_leitura()
        elif opcao == "5":
            verificar_calcada()
        elif opcao == "0":
            print("Até logo! Bom trajeto.")
            break
        else:
            print("Opção inválida. Digite um número de 0 a 5.")


if __name__ == "__main__":
    main()

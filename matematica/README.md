# AcessaBrasil · Modelagem Matemática (Differentiated Problem Solving)

Global Solution 2026.2 · CitizenTech · Prof. Rodolfo Magliari de Paiva

## Entregáveis para o Portal

| Arquivo | Formato exigido |
|---|---|
| `modelagem.py` | Código Python com cálculos, simulações e gráficos |
| `relatorio-tecnico.pdf` | Relatório técnico |

A pasta `graficos/` e o `resultados.txt` são gerados pelo próprio código.

## Problema

O semáforo sonoro do AcessaBrasil precisa (1) ser ouvido por pessoas cegas sem incomodar a vizinhança e (2) dar tempo suficiente para idosos atravessarem.

## Modelos

| Modelo | Função | Fonte da função | Dados reais |
|---|---|---|---|
| Nível do bipe pela distância | Logarítmica: L(d) = L1 − 20·log10(d) | ISO 9613-2 (divergência geométrica) e MUTCD (semáforos sonoros) | Ruído medido em 10 pontos de Irajá, Rio de Janeiro (UFRJ, 2023) |
| Tempo de travessia | Polinomial de 1º grau: T(x) = x / v | Manual Brasileiro de Sinalização de Trânsito, Vol. V | Velocidade de 1.191 idosos de São Paulo (Duim et al., 2017) |

## Principais resultados

- 95% das medições de ruído em Irajá passam de 55 dB (OMS); média de 67,8 dB.
- O volume do bipe a 1 m deve ser o ruído ambiente mais 13,3 dB: audível até 3,66 m e imperceptível a partir de 4,6 m.
- Um volume fixo seria ouvido até 36,6 m no ponto mais calmo.
- Com 15 s, o idoso médio (0,75 m/s) atravessa só 11,2 m; precisa de 0,5 s a mais por metro.

## Como rodar

```bash
pip install numpy matplotlib
cd matematica
python modelagem.py
```

## Equipe

Débora Gonçalves da Silva (RM575926), Pedro Paulo Carvalho Coutinho (RM575957), Vanessa Santos Martins de Lima Nascimento (RM576450).

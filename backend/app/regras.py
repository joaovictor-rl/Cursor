"""Regras da UFPA: conceitos, situações e o cálculo do coeficiente de rendimento (CR).

Fonte: Instrução Normativa PROEG nº 02/2008 (cálculo dos Coeficientes de Rendimento).
"""
from decimal import ROUND_HALF_UP, Decimal

# Valor numérico de cada conceito (IN 02/2008, item 3): tirar 9 ou 10 dá o mesmo Excelente.
CONCEITOS = {
    "E": {"nome": "Excelente", "faixa": "9–10", "valor": 10.0},
    "B": {"nome": "Bom", "faixa": "7–8", "valor": 7.5},
    "R": {"nome": "Regular", "faixa": "5–6", "valor": 5.0},
    "I": {"nome": "Insuficiente", "faixa": "0–4", "valor": 2.5},
}
CONCEITOS_QUE_APROVAM = {"E", "B", "R"}

# Aproveitamento, dispensa e trancamento não entram no CR (IN 02/2008, item 5)
ENTRA_NO_CR = {"aprovado", "reprovado"}
CONCLUI = {"aprovado", "dispensado"}


def normalizar_situacao(texto: str) -> str:
    """'APROVADO', 'REPROVADO POR FALTA', 'MATRICULADO'... -> aprovado, reprovado, cursando..."""
    texto = texto.strip().upper()
    if texto.startswith("APROVADO"):
        return "aprovado"
    if texto.startswith("REPROVADO"):
        return "reprovado"
    if texto.startswith(("TRANC", "CANCEL")):
        return "trancado"
    if texto.startswith("MATRIC"):
        return "cursando"
    if texto.startswith(("DISPENS", "APROVEIT", "INCORP", "CUMPR")):
        return "dispensado"
    return "outro"


def arredondar(valor: float, casas: int = 2) -> float:
    """Arredonda '5' para cima (IN 02/2008, item 4): 7,125 -> 7,13."""
    return float(Decimal(str(valor)).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP))


def calcular_cr(disciplinas: list[dict]) -> float | None:
    """Média dos conceitos ponderada pela carga horária: Σ(valor × CH) / Σ CH (IN 02/2008, item 2)."""
    avaliadas = [d for d in disciplinas if d["situacao"] in ENTRA_NO_CR and d["conceito"] in CONCEITOS]
    ch_total = sum(d["ch"] for d in avaliadas)
    if ch_total == 0:
        return None
    soma = sum(CONCEITOS[d["conceito"]]["valor"] * d["ch"] for d in avaliadas)
    return arredondar(soma / ch_total)

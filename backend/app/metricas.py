"""Métricas do painel: CR por semestre, carga horária, pendências, previsão de formatura
e o simulador do próximo semestre.

Períodos na UFPA: .2 e .4 são os regulares; .1 e .3 são intensivos (férias).
Como o SIGAA, juntamos .1 + .2 no 1º semestre do ano e .3 + .4 no 2º.
"""
import math

from .regras import CONCEITOS, CONCEITOS_QUE_APROVAM, CONCLUI, ENTRA_NO_CR, arredondar, calcular_cr


def indice_do_semestre(periodo: str) -> int:
    """'2025.2' -> 4050, '2025.4' -> 4051: um número por semestre, fácil de somar e comparar."""
    ano, numero = periodo.split(".")
    return int(ano) * 2 + (0 if int(numero) <= 2 else 1)


def rotulo_do_semestre(indice: int) -> str:
    """4050 -> '2025.2', 4051 -> '2025.4' (o período regular daquele semestre)."""
    return f"{indice // 2}.{2 if indice % 2 == 0 else 4}"


def cr_oficial_do_semestre(oficial: dict, indice: int) -> float | None:
    chave = f"{indice // 2}.{indice % 2 + 1}"  # o SIGAA escreve '2025/Sem1' -> guardamos '2025.1'
    valor = oficial["cr_semestres"].get(chave)
    return valor or None  # 0.00 = semestre ainda sem resultado


def calcular_metricas(disciplinas: list[dict], oficial: dict) -> dict:
    por_semestre: dict[int, list[dict]] = {}
    for d in disciplinas:
        por_semestre.setdefault(indice_do_semestre(d["periodo"]), []).append(d)

    semestres = []
    for indice in sorted(por_semestre):
        lista = por_semestre[indice]
        simulado = any(d.get("simulada") for d in lista)
        cr = None if simulado else cr_oficial_do_semestre(oficial, indice)
        semestres.append({
            "indice": indice,
            "periodo": rotulo_do_semestre(indice),
            "cr": cr if cr is not None else calcular_cr(lista),
            "ch_concluida": sum(d["ch"] for d in lista if d["situacao"] in CONCLUI),
            "ch_cursada": sum(d["ch"] for d in lista if d["situacao"] in CONCLUI | {"reprovado", "cursando"}),
            "ch_em_curso": sum(d["ch"] for d in lista if d["situacao"] == "cursando"),
            "aprovadas": sum(d["situacao"] == "aprovado" for d in lista),
            "reprovadas": sum(d["situacao"] == "reprovado" for d in lista),
            "trancadas": sum(d["situacao"] == "trancado" for d in lista),
            "cursando": sum(d["situacao"] == "cursando" for d in lista),
        })

    # CRG: parte do valor oficial e acrescenta só as disciplinas simuladas
    simuladas = [d for d in disciplinas if d.get("simulada") and d["situacao"] in ENTRA_NO_CR]
    if oficial["crg"] is not None:
        ch_real = sum(d["ch"] for d in disciplinas if not d.get("simulada") and d["situacao"] in ENTRA_NO_CR)
        soma = oficial["crg"] * ch_real + sum(CONCEITOS[d["conceito"]]["valor"] * d["ch"] for d in simuladas)
        ch_total = ch_real + sum(d["ch"] for d in simuladas)
        crg = arredondar(soma / ch_total, 4) if ch_total else oficial["crg"]
    else:
        crg = calcular_cr(disciplinas)

    concluidas = {d["codigo"]: d for d in disciplinas if d["situacao"] in CONCLUI}
    em_curso = {d["codigo"] for d in disciplinas if d["situacao"] == "cursando"}
    pendentes = [
        {**p, "cursando": p["matriculado"] or p["codigo"] in em_curso}
        for p in oficial["pendentes"] if p["codigo"] not in concluidas
    ]

    # carga horária: tabela oficial + o que o simulador marcou como concluído.
    # Disciplinas fora do currículo (eletivas) contam como "componentes flexibilizados", até o limite deles.
    codigos_do_curso = {p["codigo"] for p in oficial["pendentes"]}
    simuladas_ok = [d for d in concluidas.values() if d.get("simulada")]
    ch_do_curso = sum(d["ch"] for d in simuladas_ok if d["codigo"] in codigos_do_curso)
    ch_fora = sum(d["ch"] for d in simuladas_ok if d["codigo"] not in codigos_do_curso)
    ch_flexibilizada = sum(p["ch"] for p in pendentes if "flexibiliz" in p["nome"].lower())
    ch_simulada = ch_do_curso + min(ch_fora, ch_flexibilizada)
    tabela = oficial["carga_horaria"]
    if tabela:
        ch_exigida = tabela["total"]["exigida"]
        ch_integralizada = tabela["total"]["integralizada"] + ch_simulada
    else:
        ch_integralizada = sum(d["ch"] for d in concluidas.values())
        ch_exigida = ch_integralizada + sum(p["ch"] for p in pendentes)
    ch_integralizada = min(ch_integralizada, ch_exigida)

    return {
        "resumo": {
            "crg": crg,
            "crg_oficial": oficial["crg"] is not None,
            "ch_integralizada": ch_integralizada,
            "ch_exigida": ch_exigida,
            "percentual": round(ch_integralizada / ch_exigida * 100, 1) if ch_exigida else 0.0,
        },
        "semestres": semestres,
        "concluidas": sorted(sorted(concluidas.values(), key=lambda d: d["codigo"]), key=lambda d: d["periodo"], reverse=True),
        "pendentes": pendentes,
        "previsao": prever_formatura(semestres, ch_exigida - ch_integralizada, oficial["prazo"]),
    }


def prever_formatura(semestres: list[dict], ch_restante: int, prazo: str | None) -> dict:
    """Conta as disciplinas em curso como concluídas neste semestre e divide o que ainda
    faltar pela média de horas que o aluno cursa por semestre (reprovações entram na média,
    porque ocupam o semestre, mas não reduzem o que falta)."""
    atual = semestres[-1]
    ch_em_curso = atual["ch_em_curso"]
    ch_depois = max(ch_restante - ch_em_curso, 0)
    com_horas = [s["ch_cursada"] for s in semestres if s["ch_cursada"] > 0]
    ritmo = sum(com_horas) / len(com_horas) if com_horas else 0
    base = atual["indice"]  # o último semestre do histórico (em curso ou concluído)

    if ch_depois <= 0:
        restantes = 0
    elif ritmo > 0:
        restantes = math.ceil(ch_depois / ritmo)
    else:
        restantes = None

    # quantas horas por semestre seriam precisas para terminar dentro do prazo
    ritmo_para_o_prazo = None
    if prazo and ch_depois > 0:
        semestres_ate_o_prazo = indice_do_semestre(prazo) - base
        if semestres_ate_o_prazo > 0:
            ritmo_para_o_prazo = math.ceil(ch_depois / semestres_ate_o_prazo)

    return {
        "ch_restante": max(ch_restante, 0),
        "ch_em_curso": ch_em_curso,
        "ritmo": round(ritmo),
        "ritmo_para_o_prazo": ritmo_para_o_prazo,
        "semestres_restantes": restantes,
        "periodo_previsto": rotulo_do_semestre(base + restantes) if restantes is not None else None,
        "contando_de": rotulo_do_semestre(base),
        "prazo": prazo,
        "dentro_do_prazo": (base + restantes <= indice_do_semestre(prazo)) if prazo and restantes is not None else None,
    }


def simular(disciplinas: list[dict], planejadas: list[dict], oficial: dict) -> list[dict]:
    """Devolve uma cópia do histórico com o conceito escolhido em cada disciplina planejada.

    Disciplinas em curso recebem o conceito ali mesmo; as pendentes e as de fora do currículo
    (com nome e CH informados) entram no próximo semestre.
    """
    resultado = [dict(d) for d in disciplinas]
    ultimo = max(indice_do_semestre(d["periodo"]) for d in resultado)
    tem_em_curso = any(d["situacao"] == "cursando" for d in resultado)
    periodo_novo = rotulo_do_semestre(ultimo if tem_em_curso else ultimo + 1)
    pendentes = {p["codigo"]: p for p in oficial["pendentes"]}

    for plano in planejadas:
        situacao = "aprovado" if plano["conceito"] in CONCEITOS_QUE_APROVAM else "reprovado"
        alteracao = {"conceito": plano["conceito"], "situacao": situacao, "simulada": True}
        em_curso = next((d for d in resultado if d["codigo"] == plano["codigo"] and d["situacao"] == "cursando"), None)
        if em_curso:
            em_curso.update(alteracao)
        elif plano["codigo"] in pendentes:
            p = pendentes[plano["codigo"]]
            resultado.append({"periodo": periodo_novo, "codigo": p["codigo"], "nome": p["nome"], "ch": p["ch"], **alteracao})
        elif plano.get("nome") and plano.get("ch"):  # disciplina fora do currículo
            resultado.append({"periodo": periodo_novo, "codigo": plano["codigo"], "nome": plano["nome"],
                              "ch": plano["ch"], **alteracao})
    return resultado

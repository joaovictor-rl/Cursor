from app.metricas import calcular_metricas, indice_do_semestre, rotulo_do_semestre, simular
from app.regras import calcular_cr


def disciplina(periodo, codigo, ch, conceito, situacao):
    return {"periodo": periodo, "codigo": codigo, "nome": codigo, "ch": ch, "conceito": conceito, "situacao": situacao}


OFICIAL_VAZIO = {"crg": None, "cr_semestres": {}, "prazo": None, "carga_horaria": {}, "pendentes": []}


def test_semestres_juntam_periodo_intensivo_e_regular():
    assert indice_do_semestre("2026.1") == indice_do_semestre("2026.2")
    assert indice_do_semestre("2025.4") + 1 == indice_do_semestre("2026.2")
    assert rotulo_do_semestre(indice_do_semestre("2026.3")) == "2026.4"


def test_cr_e_media_ponderada_pela_carga_horaria():
    # (7,5 × 60 + 10 × 30) / 90 = 8,33
    disciplinas = [disciplina("2025.2", "A", 60, "B", "aprovado"), disciplina("2025.2", "B", 30, "E", "aprovado")]
    assert calcular_cr(disciplinas) == 8.33


def test_cr_ignora_trancadas_e_em_curso():
    disciplinas = [disciplina("2025.2", "A", 60, "R", "aprovado"), disciplina("2025.2", "B", 60, None, "trancado"),
                   disciplina("2025.4", "C", 60, None, "cursando")]
    assert calcular_cr(disciplinas) == 5.0


def test_crg_oficial_e_o_ponto_de_partida_da_simulacao():
    historico = [disciplina("2025.2", "A", 60, "B", "aprovado"), disciplina("2025.4", "C", 60, None, "cursando")]
    oficial = {**OFICIAL_VAZIO, "crg": 8.0}
    simulado = simular(historico, [{"codigo": "C", "conceito": "E"}], oficial)
    # (8,0 × 60 + 10 × 60) / 120 = 9,0
    assert calcular_metricas(simulado, oficial)["resumo"]["crg"] == 9.0


def test_simulacao_adiciona_pendente_no_proximo_semestre():
    oficial = {**OFICIAL_VAZIO, "pendentes": [{"codigo": "X", "nome": "Redes", "ch": 60, "matriculado": False}]}
    simulado = simular([disciplina("2025.4", "A", 60, "B", "aprovado")], [{"codigo": "X", "conceito": "I"}], oficial)
    assert (simulado[-1]["periodo"], simulado[-1]["situacao"]) == ("2026.2", "reprovado")


def test_previsao_de_formatura():
    historico = [disciplina("2025.2", "A", 300, "B", "aprovado"), disciplina("2025.4", "B", 300, "B", "aprovado")]
    oficial = {**OFICIAL_VAZIO, "carga_horaria": {"total": {"exigida": 1500, "integralizada": 600}}}
    previsao = calcular_metricas(historico, oficial)["previsao"]
    # faltam 900 h num ritmo de 300 h por semestre: 3 semestres depois de 2025.4 (2026.2, 2026.4 e 2027.2)
    assert (previsao["semestres_restantes"], previsao["periodo_previsto"]) == (3, "2027.2")


def test_pesos_batem_com_o_cr_do_sigaa():
    # semestre real: 150 h de B, 30 h de E e 120 h de R -> o SIGAA imprimiu CR 6,75
    disciplinas = [disciplina("2025.2", "A", 150, "B", "aprovado"), disciplina("2025.2", "B", 30, "E", "aprovado"),
                   disciplina("2025.2", "C", 120, "R", "aprovado")]
    assert calcular_cr(disciplinas) == 6.75


def test_disciplina_fora_do_curriculo_conta_como_flexibilizada():
    pendentes = [{"codigo": "FLEX", "nome": "Componentes Curriculares Flexibilizados", "ch": 240, "matriculado": False}]
    oficial = {**OFICIAL_VAZIO, "pendentes": pendentes,
               "carga_horaria": {"total": {"exigida": 1000, "integralizada": 400}}}
    historico = [disciplina("2025.4", "A", 60, "B", "aprovado")]
    simulado = simular(historico, [{"codigo": "EXTRA1", "nome": "Museu, Informação e Documentação", "ch": 60,
                                     "conceito": "E"}], oficial)
    assert calcular_metricas(simulado, oficial)["resumo"]["ch_integralizada"] == 460


def test_concluidas_mais_recentes_primeiro():
    historico = [disciplina("2024.2", "A", 60, "B", "aprovado"), disciplina("2025.4", "B", 60, "B", "aprovado")]
    concluidas = calcular_metricas(historico, OFICIAL_VAZIO)["concluidas"]
    assert [d["codigo"] for d in concluidas] == ["B", "A"]

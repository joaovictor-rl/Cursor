from pathlib import Path

import pytest

from app.parser import HistoricoInvalido, extrair_disciplinas, ler_historico

PDF_EXEMPLO = Path(__file__).resolve().parents[2] / "frontend" / "public" / "historico_ficticio.pdf"


@pytest.fixture(scope="module")
def historico():
    return ler_historico(PDF_EXEMPLO.read_bytes())


def buscar(historico, periodo, codigo):
    return next(d for d in historico["disciplinas"] if d["periodo"] == periodo and d["codigo"] == codigo)


def test_dados_do_aluno(historico):
    assert historico["aluno"]["nome"] == "MARIA FICTICIA DA SILVA"
    assert historico["aluno"]["matricula"] == "202400000001"
    assert historico["aluno"]["emitido_em"] == "26/09/2026 às 10:00"


def test_le_todas_as_disciplinas(historico):
    assert len(historico["disciplinas"]) == 33


def test_nome_vem_da_linha_de_cima(historico):
    assert buscar(historico, "2024.2", "COMP007")["nome"] == "Organização e Arquitetura de Computadores"


def test_docente_no_meio_da_linha_e_componente_eletivo(historico):
    assert buscar(historico, "2024.4", "COMP010")["ch"] == 30
    assert buscar(historico, "2025.4", "MG03014")["situacao"] == "aprovado"


def test_conceitos_e_situacoes(historico):
    assert buscar(historico, "2024.2", "COMP002")["conceito"] == "E"
    assert buscar(historico, "2024.2", "COMP004")["situacao"] == "reprovado"
    assert buscar(historico, "2025.2", "COMP016")["situacao"] == "reprovado"   # "REPROVADO POR FALTA"
    assert buscar(historico, "2024.4", "COMP013")["situacao"] == "trancado"
    em_curso = buscar(historico, "2026.2", "COMP022")
    assert (em_curso["situacao"], em_curso["conceito"]) == ("cursando", None)


def test_indices_oficiais(historico):
    oficial = historico["oficial"]
    assert oficial["crg"] == pytest.approx(7.1739)
    assert oficial["cr_semestres"]["2025.2"] == pytest.approx(7.92)
    assert oficial["prazo"] == "2027.4"
    assert oficial["carga_horaria"]["total"] == {"exigida": 3090, "integralizada": 1200}
    assert len(oficial["pendentes"]) == 24          # linhas do ENADE (0 h) ficam de fora
    estagio = next(p for p in oficial["pendentes"] if p["codigo"] == "COMP034")
    assert (estagio["ch"], estagio["matriculado"]) == (300, False)


def test_nome_em_duas_linhas():
    linhas = ["INTRODUÇÃO AO TRABALHO", "ACADÊMICO-CIENTÍFICO", "2025.2 COMP006 30 01 100,0 B APROVADO"]
    assert extrair_disciplinas(linhas)[0]["nome"] == "INTRODUÇÃO AO TRABALHO ACADÊMICO-CIENTÍFICO"


def test_pdf_invalido():
    with pytest.raises(HistoricoInvalido):
        ler_historico(b"%PDF-1.4 arquivo quebrado")


def test_codigo_em_linha_separada_com_varios_docentes():
    linhas = [
        "ANATOMIA HUMANA", "Docentes:", "ENF001",
        "2025.4 FULANO DE TAL - Titulacao: DOUTORADO 210 02A 99,2 E APROVADO",
        "CICLANA DE TAL - Titulacao: MESTRADO",
        "ENF002 HISTORIA DA ENFERMAGEM", "2025.4 60 01 100,0 B APROVADO",
        "Docente: BELTRANO - Titulacao: DOUTORADO",
        "BIOLOGIA", "ENF003", "2025.4 Docente: FULANA - Titulacao: 165 02A 100,0 R APROVADO", "DOUTORADO",
    ]
    lidas = [(d["codigo"], d["nome"], d["ch"], d["conceito"]) for d in extrair_disciplinas(linhas)]
    assert lidas == [("ENF001", "ANATOMIA HUMANA", 210, "E"), ("ENF002", "HISTORIA DA ENFERMAGEM", 60, "B"),
                     ("ENF003", "BIOLOGIA", 165, "R")]

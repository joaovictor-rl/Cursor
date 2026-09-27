from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

PDF_EXEMPLO = Path(__file__).resolve().parents[2] / "frontend" / "public" / "historico_ficticio.pdf"
cliente = TestClient(app)


def enviar(conteudo, nome="historico.pdf"):
    return cliente.post("/api/historico", files={"arquivo": (nome, conteudo, "application/pdf")})


@pytest.fixture(scope="module")
def historico():
    return enviar(PDF_EXEMPLO.read_bytes()).json()


def test_upload_devolve_metricas(historico):
    m = historico["metricas"]
    assert m["resumo"]["crg"] == pytest.approx(7.1087)
    assert m["resumo"]["percentual"] == 38.8
    assert [s["periodo"] for s in m["semestres"]] == ["2024.2", "2024.4", "2025.2", "2025.4", "2026.2"]
    assert m["previsao"]["prazo"] == "2027.4"


def test_simulacao(historico):
    em_curso = [d["codigo"] for d in historico["disciplinas"] if d["situacao"] == "cursando"]
    corpo = {"disciplinas": historico["disciplinas"], "oficial": historico["oficial"],
             "planejadas": [{"codigo": c, "conceito": "E"} for c in em_curso]}
    resposta = cliente.post("/api/simulacao", json=corpo)
    assert resposta.status_code == 200
    antes, depois = resposta.json()["antes"], resposta.json()["depois"]
    assert depois["resumo"]["crg"] > antes["resumo"]["crg"]
    assert depois["resumo"]["ch_integralizada"] == antes["resumo"]["ch_integralizada"] + 6 * 60


def test_simulacao_rejeita_conceito_invalido(historico):
    corpo = {"disciplinas": historico["disciplinas"], "oficial": historico["oficial"],
             "planejadas": [{"codigo": "COMP022", "conceito": "X"}]}
    assert cliente.post("/api/simulacao", json=corpo).status_code == 422


def test_rejeita_arquivo_que_nao_e_pdf():
    assert enviar(b"nome,nota\nfulano,10", "notas.csv").status_code == 415


def test_rejeita_arquivo_grande():
    assert enviar(b"%PDF" + b"0" * (5 * 1024 * 1024)).status_code == 413


def test_pdf_sem_disciplinas():
    assert enviar(b"%PDF-1.4 vazio").status_code == 422


def test_cabecalhos_de_seguranca():
    resposta = cliente.get("/api/saude")
    assert resposta.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]

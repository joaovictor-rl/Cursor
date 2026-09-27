"""API do Cursor (FastAPI). Também entrega o site já compilado (frontend/dist).

Privacidade: o PDF enviado é lido em memória e descartado ao fim da requisição.
A API não guarda nada: o navegador reenvia o histórico quando quer simular.
"""
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .metricas import calcular_metricas, simular
from .parser import HistoricoInvalido, ler_historico

TAMANHO_MAXIMO = 5 * 1024 * 1024  # 5 MB
PASTA_DO_SITE = Path(__file__).resolve().parents[2] / "frontend" / "dist"

Conceito = Literal["E", "B", "R", "I"]
Situacao = Literal["aprovado", "reprovado", "trancado", "cursando", "dispensado", "outro"]


class Disciplina(BaseModel):
    periodo: str = Field(pattern=r"^\d{4}\.[1-4]$")
    codigo: str = Field(max_length=20)
    nome: str = Field(default="", max_length=200)
    ch: int = Field(ge=0, le=2000)
    conceito: Conceito | None = None
    situacao: Situacao


class Pendente(BaseModel):
    codigo: str = Field(max_length=20)
    nome: str = Field(max_length=200)
    ch: int = Field(ge=0, le=2000)
    matriculado: bool = False


class Oficial(BaseModel):
    crg: float | None = Field(default=None, ge=0, le=10)
    cr_semestres: dict[str, float] = Field(default_factory=dict, max_length=40)
    prazo: str | None = Field(default=None, max_length=10)
    carga_horaria: dict[str, dict[str, int]] = Field(default_factory=dict, max_length=10)
    pendentes: list[Pendente] = Field(default_factory=list, max_length=200)


class Planejada(BaseModel):
    codigo: str = Field(max_length=20)
    conceito: Conceito
    nome: str | None = Field(default=None, max_length=200)  # só para disciplina fora do currículo
    ch: int | None = Field(default=None, ge=1, le=400)


class PedidoDeSimulacao(BaseModel):
    disciplinas: list[Disciplina] = Field(min_length=1, max_length=300)
    oficial: Oficial
    planejadas: list[Planejada] = Field(min_length=1, max_length=30)


app = FastAPI(title="Cursor", docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")


@app.middleware("http")
async def cabecalhos_de_seguranca(request, call_next):
    resposta = await call_next(request)
    resposta.headers["X-Content-Type-Options"] = "nosniff"
    resposta.headers["X-Frame-Options"] = "DENY"
    resposta.headers["Referrer-Policy"] = "no-referrer"
    if not request.url.path.startswith("/api/docs"):
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "font-src 'self'; frame-ancestors 'none'"
        )
    return resposta


@app.get("/api/saude")
def saude():
    return {"status": "ok"}


@app.post("/api/historico")
def enviar_historico(arquivo: UploadFile = File(...)):
    conteudo = arquivo.file.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(413, "Arquivo maior que 5 MB.")
    if not conteudo.startswith(b"%PDF"):
        raise HTTPException(415, "Envie um arquivo PDF.")
    try:
        historico = ler_historico(conteudo)
    except HistoricoInvalido as erro:
        raise HTTPException(422, str(erro)) from erro
    historico["metricas"] = calcular_metricas(historico["disciplinas"], historico["oficial"])
    return historico


@app.post("/api/simulacao")
def simular_semestre(pedido: PedidoDeSimulacao):
    disciplinas = [d.model_dump() for d in pedido.disciplinas]
    oficial = pedido.oficial.model_dump()
    simuladas = simular(disciplinas, [p.model_dump() for p in pedido.planejadas], oficial)
    return {"antes": calcular_metricas(disciplinas, oficial), "depois": calcular_metricas(simuladas, oficial)}


if PASTA_DO_SITE.joinpath("index.html").exists():
    app.mount("/", StaticFiles(directory=PASTA_DO_SITE, html=True), name="site")

"""Lê o PDF do histórico do SIGAA/UFPA e devolve os dados do aluno, as disciplinas
e os índices oficiais. O PDF é lido da memória: nada é salvo em disco."""
import io
import re

import pandas as pd
import pdfplumber

from .regras import CONCEITOS, normalizar_situacao

MAX_PAGINAS = 20

# No SIGAA o nome da disciplina fica numa linha própria, acima da linha com o código:
#   ALGORITMOS
#   2025.2 COMP001 60 02 100,0 B APROVADO
#   2025.4 COMP010 Docente: FULANO - Titulacao: DOUTORADO 30 02 100,0 B APROVADO
#   2026.4 # MG03014 60 02 100,0 - MATRICULADO
# Colunas: período, (símbolo), código, (docente), CH, turma, frequência, conceito, situação.
LINHA_DISCIPLINA = re.compile(
    r"^(?P<periodo>\d{4}\.[1-4]) (?:[*&#@§] )?(?P<codigo>[A-Z]{2,}\d{2,}\w*) (?:Docente:.*? )?"
    r"(?P<ch>\d{1,4}) \S+ \S+ (?P<conceito>\S+) (?P<situacao>[A-ZÀ-Ü ]+)$"
)
LINHA_DE_NOME = re.compile(r"^[A-ZÀ-Ü0-9][A-ZÀ-Ü0-9 ,.\-()/&']*$")

DADOS_DO_ALUNO = {
    "nome": re.compile(r"Nome: (.+?) Matr[íi]cula:"),
    "matricula": re.compile(r"Matr[íi]cula: (\d+)"),
    "curso": re.compile(r"Curso: (.+)$"),
    "emitido_em": re.compile(r"Emitido em: (\d{2}/\d{2}/\d{4}(?: às \d{2}:\d{2})?)"),
}
CRG = re.compile(r"CRG: (\d+\.\d+)")
CR_SEMESTRE = re.compile(r"(\d{4})/Sem(\d): (\d+\.\d+)")
PRAZO = re.compile(r"Prazo para Conclus[ãa]o: (\d{4}\.\d)")
TABELA_CH = re.compile(r"^(Exigido|Integralizado) ((?:\d+ h ?){5})$")
PENDENTE = re.compile(r"^(?P<codigo>[A-Z]{2,}\d+\w*) (?P<nome>.+?) (?P<ch>\d+) h$")
COMPONENTES_CH = ["obrigatoria", "optativa", "extensao", "complementar", "total"]


PALAVRAS_MINUSCULAS = {"a", "o", "e", "de", "da", "do", "das", "dos", "em", "na", "no", "para", "ao"}
ROMANOS = {"I", "II", "III", "IV", "V"}


class HistoricoInvalido(ValueError):
    pass


def nome_legivel(nome: str) -> str:
    """'ESTRUTURAS DE DADOS II' -> 'Estruturas de Dados II'."""
    palavras = []
    for i, palavra in enumerate(nome.split()):
        if palavra in ROMANOS:
            palavras.append(palavra)
        elif i > 0 and palavra.lower() in PALAVRAS_MINUSCULAS:
            palavras.append(palavra.lower())
        else:
            palavras.append(palavra.capitalize())
    return " ".join(palavras)


def ler_linhas(pdf_bytes: bytes) -> list[str]:
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if len(pdf.pages) > MAX_PAGINAS:
                raise HistoricoInvalido("PDF com páginas demais para um histórico.")
            texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)
    except HistoricoInvalido:
        raise
    except Exception as erro:
        raise HistoricoInvalido("Não foi possível ler o PDF.") from erro
    return [" ".join(linha.split()) for linha in texto.splitlines() if linha.strip()]


def extrair_disciplinas(linhas: list[str]) -> list[dict]:
    disciplinas, nome = [], []
    for linha in linhas:
        achado = LINHA_DISCIPLINA.match(linha)
        if achado:
            conceito = achado["conceito"] if achado["conceito"] in CONCEITOS else None
            disciplinas.append({
                "periodo": achado["periodo"], "codigo": achado["codigo"], "nome": " ".join(nome[-3:]),
                "ch": int(achado["ch"]), "conceito": conceito,
                "situacao": normalizar_situacao(achado["situacao"]),
            })
            nome = []
        elif LINHA_DE_NOME.match(linha):
            nome.append(linha)
        else:
            nome = []
    return disciplinas


def extrair_oficial(linhas: list[str]) -> dict:
    """Índices que o próprio SIGAA calcula e imprime no fim do histórico."""
    oficial = {"crg": None, "cr_semestres": {}, "prazo": None, "carga_horaria": {}, "pendentes": []}
    tabela, na_lista_de_pendentes = {}, False
    for linha in linhas:
        if achado := CRG.search(linha):
            oficial["crg"] = float(achado[1])
        if achado := PRAZO.search(linha):
            oficial["prazo"] = achado[1]
        for ano, semestre, valor in CR_SEMESTRE.findall(linha):
            oficial["cr_semestres"][f"{ano}.{semestre}"] = float(valor)
        if achado := TABELA_CH.match(linha):
            tabela[achado[1]] = [int(h) for h in re.findall(r"\d+", achado[2])]

        if linha.startswith("Componentes Curriculares Obrigatórios Pendentes"):
            na_lista_de_pendentes = True
        elif linha.startswith(("Para verificar", "Atenção")):
            na_lista_de_pendentes = False
        elif na_lista_de_pendentes and (achado := PENDENTE.match(linha)):
            nome = achado["nome"]
            oficial["pendentes"].append({
                "codigo": achado["codigo"], "nome": nome_legivel(nome.removesuffix(" Matriculado")),
                "ch": int(achado["ch"]), "matriculado": nome.endswith(" Matriculado"),
            })

    if "Exigido" in tabela and "Integralizado" in tabela:
        oficial["carga_horaria"] = {
            componente: {"exigida": exigida, "integralizada": integralizada}
            for componente, exigida, integralizada in zip(COMPONENTES_CH, tabela["Exigido"], tabela["Integralizado"])
        }
    return oficial


def ler_historico(pdf_bytes: bytes) -> dict:
    linhas = ler_linhas(pdf_bytes)
    disciplinas = pd.DataFrame(extrair_disciplinas(linhas))
    if disciplinas.empty:
        raise HistoricoInvalido("Nenhuma disciplina encontrada. Envie o PDF do histórico emitido pelo SIGAA.")

    # limpeza com pandas: nomes padronizados, sem linhas repetidas e em ordem cronológica
    disciplinas["nome"] = disciplinas["nome"].map(nome_legivel)
    disciplinas = disciplinas.drop_duplicates().sort_values(["periodo", "codigo"])
    disciplinas = disciplinas.astype(object).where(disciplinas.notna(), None)

    aluno = {campo: None for campo in DADOS_DO_ALUNO}
    for linha in linhas:
        for campo, regex in DADOS_DO_ALUNO.items():
            if aluno[campo] is None and (achado := regex.search(linha)):
                aluno[campo] = achado[1].strip()

    return {"aluno": aluno, "disciplinas": disciplinas.to_dict("records"), "oficial": extrair_oficial(linhas)}

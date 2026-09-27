export const CONCEITOS = [
  { sigla: "I", nome: "Insuficiente", faixa: "0–4" },
  { sigla: "R", nome: "Regular", faixa: "5–6" },
  { sigla: "B", nome: "Bom", faixa: "7–8" },
  { sigla: "E", nome: "Excelente", faixa: "9–10" },
];

export const nomeDoConceito = (sigla) => CONCEITOS.find((c) => c.sigla === sigla)?.nome;

export const numero = (valor, casas = 2) =>
  valor == null ? "—" : Number(valor).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

export const horas = (valor) => `${Number(valor).toLocaleString("pt-BR")} h`;

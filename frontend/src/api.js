async function pedir(url, opcoes) {
  const resposta = await fetch(url, opcoes);
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    throw new Error(typeof corpo.detail === "string" ? corpo.detail : "Não foi possível processar o pedido.");
  }
  return corpo;
}

export function enviarHistorico(arquivo) {
  const formulario = new FormData();
  formulario.append("arquivo", arquivo);
  return pedir("/api/historico", { method: "POST", body: formulario });
}

export function simular({ disciplinas, oficial }, planejadas) {
  return pedir("/api/simulacao", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      disciplinas,
      oficial,
      planejadas: planejadas.map(({ codigo, conceito, nome, ch }) => ({ codigo, conceito, nome, ch })),
    }),
  });
}

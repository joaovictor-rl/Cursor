import { horas } from "../formato";

const valorDoPeriodo = (periodo) => Number(periodo?.replace(".", ""));

export default function Previsao({ previsao }) {
  const atrasado = previsao.prazo && valorDoPeriodo(previsao.periodo_previsto) > valorDoPeriodo(previsao.prazo);
  return (
    <section className="bloco">
      <h2>Previsão de formatura</h2>
      <p className="bloco-dica">Carga horária que falta ÷ sua média de horas concluídas por semestre</p>
      <div className="previsao-destaque">
        <span className="previsao-periodo">{previsao.periodo_previsto ?? "—"}</span>
        {previsao.prazo && (
          <span className={`selo ${atrasado ? "alerta" : "ok"}`}>
            {atrasado ? "▲ depois do prazo" : "✓ dentro do prazo"} ({previsao.prazo})
          </span>
        )}
      </div>
      <dl className="previsao-lista">
        <div><dt>Falta cumprir</dt><dd>{horas(previsao.ch_restante)}</dd></div>
        <div><dt>Ritmo médio</dt><dd>{previsao.ritmo} h/semestre</dd></div>
        <div><dt>Semestres restantes</dt><dd>{previsao.semestres_restantes ?? "—"}</dd></div>
        <div><dt>Contando a partir de</dt><dd>{previsao.contando_de}</dd></div>
      </dl>
    </section>
  );
}

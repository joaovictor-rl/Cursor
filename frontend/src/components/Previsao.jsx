import { horas } from "../formato";

export default function Previsao({ previsao }) {
  const atrasado = previsao.dentro_do_prazo === false;
  return (
    <section className="bloco">
      <h2>Previsão de formatura</h2>
      <p className="bloco-dica">
        Contando que você passe no que está cursando em {previsao.contando_de}: horas que ainda faltam ÷ média de horas que você cursa por semestre
      </p>
      <div className="previsao-destaque">
        <span className="previsao-periodo">{previsao.periodo_previsto ?? "—"}</span>
        {previsao.prazo && previsao.dentro_do_prazo != null && (
          <span className={`selo ${atrasado ? "alerta" : "ok"}`}>
            {atrasado ? "▲ depois do prazo" : "✓ dentro do prazo"} ({previsao.prazo})
          </span>
        )}
      </div>
      <dl className="previsao-lista">
        <div><dt>Falta cumprir</dt><dd>{horas(previsao.ch_restante)}</dd></div>
        <div><dt>Seu ritmo</dt><dd>{previsao.ritmo} h/semestre</dd></div>
        <div><dt>Semestres depois deste</dt><dd>{previsao.semestres_restantes ?? "—"}</dd></div>
        <div><dt>Para terminar no prazo</dt><dd>{previsao.ritmo_para_o_prazo ? `${previsao.ritmo_para_o_prazo} h/semestre` : "—"}</dd></div>
      </dl>
    </section>
  );
}

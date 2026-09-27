import { horas, numero } from "../formato";

export default function ProgressoCH({ resumo, concluidas, pendentes }) {
  return (
    <section className="bloco">
      <h2>Carga horária</h2>
      <p className="bloco-dica">Cumprida × exigida pelo currículo, segundo o SIGAA</p>
      <div className="progresso-topo">
        <span>{horas(resumo.ch_integralizada)} de {horas(resumo.ch_exigida)}</span>
        <strong>{numero(resumo.percentual, 1)}%</strong>
      </div>
      <div className="barra" role="progressbar" aria-valuenow={resumo.percentual} aria-valuemin={0} aria-valuemax={100}>
        <div className="barra-preenchida" style={{ width: `${resumo.percentual}%` }} />
      </div>
      <dl className="previsao-lista progresso-lista">
        <div><dt>Disciplinas concluídas</dt><dd>{concluidas}</dd></div>
        <div><dt>Componentes pendentes</dt><dd>{pendentes}</dd></div>
      </dl>
    </section>
  );
}

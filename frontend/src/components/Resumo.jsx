import { horas, numero } from "../formato";

export default function Resumo({ resumo, previsao }) {
  return (
    <section className="resumo" aria-label="Resumo">
      <div className="cartao">
        <span className="cartao-rotulo">CRG</span>
        <span className="cartao-valor">{numero(resumo.crg)}</span>
        <span className="cartao-detalhe">{resumo.crg_oficial ? `oficial do SIGAA: ${numero(resumo.crg, 4)}` : "estimado pelos conceitos"}</span>
      </div>
      <div className="cartao">
        <span className="cartao-rotulo">Curso concluído</span>
        <span className="cartao-valor">{numero(resumo.percentual, 1)}%</span>
        <span className="cartao-detalhe">{horas(resumo.ch_integralizada)} de {horas(resumo.ch_exigida)}</span>
      </div>
      <div className="cartao">
        <span className="cartao-rotulo">Previsão de formatura</span>
        <span className="cartao-valor">{previsao.periodo_previsto ?? "—"}</span>
        <span className="cartao-detalhe">prazo do curso: {previsao.prazo ?? "—"}</span>
      </div>
    </section>
  );
}

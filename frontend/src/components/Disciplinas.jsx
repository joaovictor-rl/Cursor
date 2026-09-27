import { useState } from "react";
import { horas, nomeDoConceito } from "../formato";

export default function Disciplinas({ concluidas, pendentes }) {
  const [aba, setAba] = useState("concluidas");
  const lista = aba === "concluidas" ? concluidas : pendentes;
  const total = lista.reduce((soma, d) => soma + d.ch, 0);

  return (
    <section className="bloco largo">
      <div className="bloco-cabecalho">
        <div>
          <h2>Disciplinas</h2>
          <p className="bloco-dica">{lista.length} {aba === "concluidas" ? "concluídas" : "não concluídas"} · {horas(total)}</p>
        </div>
        <div className="filtros" role="tablist">
          <button role="tab" aria-selected={aba === "concluidas"} className={`filtro ${aba === "concluidas" ? "ativo" : ""}`}
                  onClick={() => setAba("concluidas")}>Concluídas ({concluidas.length})</button>
          <button role="tab" aria-selected={aba === "pendentes"} className={`filtro ${aba === "pendentes" ? "ativo" : ""}`}
                  onClick={() => setAba("pendentes")}>Não concluídas ({pendentes.length})</button>
        </div>
      </div>

      <div className="tabela-rolagem">
        <table>
          <thead>
            <tr>
              {aba === "concluidas" && <th>Período</th>}
              <th>Código</th><th>Disciplina</th><th>CH</th><th>{aba === "concluidas" ? "Conceito" : "Situação"}</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((d) => (
              <tr key={d.codigo}>
                {aba === "concluidas" && <td className="mono">{d.periodo}</td>}
                <td className="mono">{d.codigo}</td>
                <td>{d.nome}</td>
                <td>{d.ch} h</td>
                <td>
                  {aba === "concluidas" ? (
                    d.conceito ? <span className={`conceito conceito-${d.conceito}`}>{nomeDoConceito(d.conceito)}</span> : "—"
                  ) : d.cursando ? (
                    <span className="selo info">● cursando</span>
                  ) : (
                    <span className="selo neutro">○ a cursar</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

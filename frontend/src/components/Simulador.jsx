import { useState } from "react";
import { simular } from "../api";
import { CONCEITOS, numero } from "../formato";

const OUTRA = "__outra__";

export default function Simulador({ historico }) {
  const emCurso = historico.disciplinas.filter((d) => d.situacao === "cursando");
  const aCursar = historico.metricas.pendentes.filter((p) => !p.cursando);
  const conhecidas = [...emCurso, ...aCursar];

  const [planejadas, setPlanejadas] = useState(emCurso.map((d) => ({ codigo: d.codigo, conceito: "B" })));
  const [escolhida, setEscolhida] = useState("");
  const [extra, setExtra] = useState({ nome: "", ch: "" });
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState("");

  const dadosDe = (plano) => conhecidas.find((d) => d.codigo === plano.codigo) ?? plano;
  const disponiveis = aCursar.filter((p) => !planejadas.some((x) => x.codigo === p.codigo));

  function mudar(novaLista) {
    setPlanejadas(novaLista);
    setResultado(null);
  }

  function adicionar() {
    if (escolhida === OUTRA) {
      const numeroExtra = planejadas.filter((p) => p.extra).length + 1;
      mudar([...planejadas, { codigo: `EXTRA${numeroExtra}`, nome: extra.nome.trim(), ch: Number(extra.ch), conceito: "B", extra: true }]);
      setExtra({ nome: "", ch: "" });
    } else {
      mudar([...planejadas, { codigo: escolhida, conceito: "B" }]);
    }
    setEscolhida("");
  }

  async function rodar() {
    setErro("");
    try {
      setResultado(await simular(historico, planejadas));
    } catch (e) {
      setErro(e.message);
    }
  }

  const extraValida = extra.nome.trim() && Number(extra.ch) >= 1 && Number(extra.ch) <= 400;
  const podeAdicionar = escolhida && (escolhida !== OUTRA || extraValida);

  return (
    <section className="bloco largo">
      <h2>Simulador do próximo semestre</h2>
      <p className="bloco-dica">
        Escolha o conceito que você espera em cada disciplina. Cada conceito tem um peso fixo no CRG, como no SIGAA.
      </p>

      <div className="simulador">
        <div className="simulador-lista">
          {planejadas.length === 0 && <p className="vazio">Adicione disciplinas para simular.</p>}
          {planejadas.map((p) => (
            <div className="plano" key={p.codigo}>
              <div className="plano-nome">
                {!p.extra && <span className="mono">{p.codigo}</span>} {dadosDe(p).nome}
                <span className="plano-ch">{dadosDe(p).ch} h</span>
                {p.extra && <span className="selo extra">fora do currículo</span>}
              </div>
              <div className="seletor-conceito" role="radiogroup" aria-label={`Conceito em ${dadosDe(p).nome}`}>
                {CONCEITOS.map((c) => (
                  <button key={c.sigla} type="button" role="radio" aria-checked={p.conceito === c.sigla}
                          className={`opcao-conceito op-${c.sigla} ${p.conceito === c.sigla ? "marcado" : ""}`}
                          onClick={() => mudar(planejadas.map((x) => (x.codigo === p.codigo ? { ...x, conceito: c.sigla } : x)))}>
                    <strong>{c.nome}</strong>
                    <small>{c.faixa}</small>
                  </button>
                ))}
              </div>
              <button className="remover" aria-label={`Remover ${dadosDe(p).nome}`}
                      onClick={() => mudar(planejadas.filter((x) => x.codigo !== p.codigo))}>✕</button>
            </div>
          ))}

          <div className="simulador-adicionar">
            <select value={escolhida} onChange={(e) => setEscolhida(e.target.value)} aria-label="Disciplina">
              <option value="">Adicionar disciplina…</option>
              {disponiveis.map((p) => (
                <option key={p.codigo} value={p.codigo}>{p.codigo} — {p.nome} ({p.ch} h)</option>
              ))}
              <option value={OUTRA}>Outra disciplina (fora do currículo)…</option>
            </select>
            <button className="botao secundario" disabled={!podeAdicionar} onClick={adicionar}>Adicionar</button>
            <button className="botao" onClick={rodar} disabled={planejadas.length === 0}>Simular</button>
          </div>

          {escolhida === OUTRA && (
            <div className="form-extra">
              <label>
                Nome da disciplina
                <input value={extra.nome} maxLength={200} placeholder="ex.: Museu, Informação e Documentação"
                       onChange={(e) => setExtra({ ...extra, nome: e.target.value })} />
              </label>
              <label className="campo-ch">
                CH (horas)
                <input type="number" min="1" max="400" value={extra.ch} placeholder="60"
                       onChange={(e) => setExtra({ ...extra, ch: e.target.value })} />
              </label>
            </div>
          )}
          {erro && <p className="erro">{erro}</p>}
        </div>

        <div className="simulador-resultado" aria-live="polite">
          {resultado ? (
            <>
              <Comparacao rotulo="CRG" antes={numero(resultado.antes.resumo.crg)} depois={numero(resultado.depois.resumo.crg)}
                          diferenca={resultado.depois.resumo.crg - resultado.antes.resumo.crg} />
              <Comparacao rotulo="Curso concluído" antes={`${numero(resultado.antes.resumo.percentual, 1)}%`}
                          depois={`${numero(resultado.depois.resumo.percentual, 1)}%`} />
              <Comparacao rotulo="Previsão de formatura" antes={resultado.antes.previsao.periodo_previsto}
                          depois={resultado.depois.previsao.periodo_previsto} />
            </>
          ) : (
            <p className="vazio">O resultado aparece aqui.</p>
          )}
        </div>
      </div>
    </section>
  );
}

function Comparacao({ rotulo, antes, depois, diferenca }) {
  return (
    <div className="comparacao">
      <span className="cartao-rotulo">{rotulo}</span>
      <span className="comparacao-valores">
        {antes ?? "—"} <span className="seta">→</span> <strong>{depois ?? "—"}</strong>
        {diferenca != null && Math.abs(diferenca) >= 0.005 && (
          <span className={`delta ${diferenca > 0 ? "sobe" : "desce"}`}>
            {diferenca > 0 ? "▲" : "▼"} {numero(Math.abs(diferenca))}
          </span>
        )}
      </span>
    </div>
  );
}

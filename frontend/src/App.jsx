import { useEffect, useState } from "react";
import { enviarHistorico } from "./api";
import Upload from "./components/Upload";
import Resumo from "./components/Resumo";
import GraficoCR from "./components/GraficoCR";
import GraficoSemestres from "./components/GraficoSemestres";
import ProgressoCH from "./components/ProgressoCH";
import Previsao from "./components/Previsao";
import Simulador from "./components/Simulador";
import Disciplinas from "./components/Disciplinas";
import Logo from "./components/Logo";

const HOJE = new Date().toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" });

export default function App() {
  const [historico, setHistorico] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  async function processar(arquivo) {
    setErro("");
    setCarregando(true);
    try {
      setHistorico(await enviarHistorico(arquivo));
    } catch (e) {
      setErro(e.message === "Failed to fetch" ? "Não foi possível falar com o servidor." : e.message);
    } finally {
      setCarregando(false);
    }
  }

  async function usarExemplo() {
    const resposta = await fetch("/historico_ficticio.pdf");
    processar(new File([await resposta.blob()], "historico_ficticio.pdf", { type: "application/pdf" }));
  }

  const m = historico?.metricas;

  // Na tela inicial tudo cabe na janela: a rolagem só existe depois que o painel aparece.
  useEffect(() => {
    document.body.classList.toggle("sem-rolagem", !historico);
  }, [historico]);

  return (
    <div className={`pagina ${historico ? "" : "inicial"}`}>
      <header className="jornal">
        <div className="jornal-faixa">
          <span>Edição de {HOJE}</span>
          <span className="jornal-faixa-centro">O jornal da sua trajetória acadêmica</span>
          <span>Sistemas de Informação · UFPA</span>
        </div>
        <div className="jornal-manchete">
          <h1 className="logo"><Logo /></h1>
        </div>
        <div className="jornal-sub">
          <p className="subtitulo">Envie o histórico do SIGAA e leia, em uma página, em que ponto do curso você está.</p>
          {historico && (
            <button className="botao secundario" onClick={() => setHistorico(null)}>Enviar outro histórico</button>
          )}
        </div>
      </header>

      {!historico && <Upload aoEnviar={processar} aoUsarExemplo={usarExemplo} carregando={carregando} erro={erro} />}

      {m && (
        <main className="painel">
          <p className="aluno">
            <strong>{historico.aluno.nome}</strong> · matrícula {historico.aluno.matricula} · {historico.aluno.curso}
            {historico.aluno.emitido_em && <> · histórico emitido em {historico.aluno.emitido_em}</>}
          </p>
          <Resumo resumo={m.resumo} previsao={m.previsao} />
          <div className="grade">
            <GraficoCR semestres={m.semestres} crg={m.resumo.crg} />
            <GraficoSemestres semestres={m.semestres} />
            <ProgressoCH resumo={m.resumo} concluidas={m.concluidas.length} pendentes={m.pendentes.length} />
            <Previsao previsao={m.previsao} />
          </div>
          <Simulador historico={historico} />
          <Disciplinas concluidas={m.concluidas} pendentes={m.pendentes} />
        </main>
      )}

      <footer className="rodape">
        © {new Date().getFullYear()} João Victor R. Lisboa · Projeto independente, sem vínculo oficial com a UFPA.
      </footer>
    </div>
  );
}

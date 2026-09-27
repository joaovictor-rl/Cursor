import { useRef, useState } from "react";

export default function Upload({ aoEnviar, aoUsarExemplo, carregando, erro }) {
  const [arrastando, setArrastando] = useState(false);
  const campoDeArquivo = useRef(null);

  function escolher(arquivos) {
    if (arquivos?.[0]) aoEnviar(arquivos[0]);
  }

  return (
    <section className="upload-area">
      <p className="abertura">
        <span className="capitular" aria-hidden="true">O</span>
        histórico do SIGAA é uma lista longa de disciplinas. Aqui ele vira uma página só: seu CRG, quanto do curso
        você já cumpriu, o que falta e quando você deve se formar — com um simulador para planejar o próximo semestre.
      </p>

      <div
        className={`dropzone ${arrastando ? "ativa" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => campoDeArquivo.current.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && campoDeArquivo.current.click()}
        onDragOver={(e) => { e.preventDefault(); setArrastando(true); }}
        onDragLeave={() => setArrastando(false)}
        onDrop={(e) => { e.preventDefault(); setArrastando(false); escolher(e.dataTransfer.files); }}
      >
        <input ref={campoDeArquivo} type="file" accept="application/pdf" hidden onChange={(e) => escolher(e.target.files)} />
        <div className="icone-upload" aria-hidden="true">↓</div>
        <p className="dropzone-titulo">{carregando ? "Lendo o histórico…" : "Arraste o PDF do seu histórico do SIGAA aqui"}</p>
        <p className="dropzone-dica">ou clique para escolher o arquivo (até 5 MB)</p>
      </div>

      {erro && <p className="erro" role="alert">{erro}</p>}

      <div className="upload-rodape">
        <p className="privacidade">
          🔒 <strong>Privacidade:</strong> o PDF é lido em memória e descartado ao fim da leitura. Nada do seu histórico
          fica salvo no servidor.
        </p>
        <button className="botao" onClick={aoUsarExemplo} disabled={carregando}>Ver com um histórico fictício</button>
      </div>

      <details className="como-baixar">
        <summary>Como baixar o histórico no SIGAA?</summary>
        <p>SIGAA → Portal do Discente → Ensino → Emitir Histórico. Salve o PDF e envie aqui.</p>
      </details>
    </section>
  );
}

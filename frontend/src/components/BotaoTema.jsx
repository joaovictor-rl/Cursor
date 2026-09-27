import { useEffect, useState } from "react";

function temaSalvo() {
  try {
    return localStorage.getItem("tema") === "escuro" ? "escuro" : "claro";
  } catch {
    return "claro";
  }
}

export default function BotaoTema() {
  const [tema, setTema] = useState(temaSalvo);
  const escuro = tema === "escuro";

  useEffect(() => {
    document.documentElement.dataset.tema = tema;
    try {
      localStorage.setItem("tema", tema);
    } catch {
      /* navegador sem armazenamento: o tema só não fica lembrado */
    }
  }, [tema]);

  return (
    <button type="button" className="botao-tema" onClick={() => setTema(escuro ? "claro" : "escuro")}
            aria-label={escuro ? "Mudar para o tema claro" : "Mudar para o tema escuro"}
            title={escuro ? "Tema claro" : "Tema escuro"}>
      <svg viewBox="0 0 24 24" fill={escuro ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8"
           strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z" />
      </svg>
    </button>
  );
}

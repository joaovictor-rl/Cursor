import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const EIXO = { fill: "var(--texto-2)", fontSize: 13 };
const SERIES = [
  { chave: "aprovadas", nome: "Aprovadas", cor: "var(--serie-1)" },
  { chave: "reprovadas", nome: "Reprovadas", cor: "var(--serie-2)" },
  { chave: "trancadas", nome: "Trancadas", cor: "var(--neutra)" },
];

export default function GraficoSemestres({ semestres }) {
  const dados = semestres.filter((s) => s.cursando === 0);
  return (
    <section className="bloco">
      <h2>Aprovações e reprovações</h2>
      <p className="bloco-dica">Quantidade de disciplinas por semestre</p>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={dados} margin={{ top: 8, right: 16, left: -24, bottom: 0 }}>
          <CartesianGrid stroke="var(--grade)" vertical={false} />
          <XAxis dataKey="periodo" tick={EIXO} stroke="var(--eixo)" />
          <YAxis allowDecimals={false} tick={EIXO} stroke="var(--eixo)" />
          <Tooltip cursor={{ fill: "var(--grade)" }} />
          <Legend />
          {SERIES.map((s) => (
            <Bar key={s.chave} dataKey={s.chave} name={s.nome} stackId="total" fill={s.cor}
                 stroke="var(--papel)" strokeWidth={2} maxBarSize={40} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}

import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { numero } from "../formato";

const EIXO = { fill: "var(--texto-2)", fontSize: 13 };

export default function GraficoCR({ semestres, crg }) {
  const dados = semestres.filter((s) => s.cr !== null);
  return (
    <section className="bloco">
      <h2>CR ao longo dos semestres</h2>
      <p className="bloco-dica">Linha: CR de cada semestre · Tracejado: seu CRG (média de todo o curso)</p>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={dados} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
          <CartesianGrid stroke="var(--grade)" vertical={false} />
          <XAxis dataKey="periodo" tick={EIXO} stroke="var(--eixo)" />
          <YAxis domain={[0, 10]} ticks={[0, 2, 4, 6, 8, 10]} tick={EIXO} stroke="var(--eixo)" />
          <Tooltip formatter={(valor) => numero(valor)} cursor={{ stroke: "var(--eixo)" }} />
          <ReferenceLine y={crg} stroke="var(--serie-1)" strokeWidth={2} strokeDasharray="6 4"
                         label={{ value: `CRG ${numero(crg)}`, position: "insideTopRight", ...EIXO }} />
          <Line type="monotone" dataKey="cr" name="CR do semestre" stroke="var(--serie-2)" strokeWidth={2}
                dot={{ r: 4, fill: "var(--papel)", strokeWidth: 2 }} activeDot={{ r: 6, fill: "var(--papel)" }} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}

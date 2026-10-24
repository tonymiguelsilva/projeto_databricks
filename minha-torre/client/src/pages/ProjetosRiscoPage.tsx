import { useEffect, useState } from 'react';
import { Alert, AlertDescription, Badge, Card, CardContent, CardHeader, CardTitle, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, useAnalyticsQuery } from '@databricks/appkit-ui/react';
import { Carregando, Erro, Fonte, Vazio } from '../components/Estados';
import { classeSituacao, indice, inteiro, moeda, percentual } from '../lib/formatos';

type Score = { projeto_id: string; prob_estouro_30d: number | string | null; faixa_risco: string | null };
type RespostaScore = { disponivel: boolean; linhas: Score[] };
function respostaScore(valor: unknown): RespostaScore {
  if (typeof valor !== 'object' || valor === null) return { disponivel: false, linhas: [] };
  const resposta = valor as { disponivel?: unknown; linhas?: unknown };
  return { disponivel: resposta.disponivel === true, linhas: Array.isArray(resposta.linhas) ? resposta.linhas as Score[] : [] };
}
function Kpi({ titulo, valor }: { titulo: string; valor: string }) { return <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">{titulo}</CardTitle></CardHeader><CardContent><div className="text-2xl font-semibold tabular-nums">{valor}</div></CardContent></Card>; }

export function ProjetosRiscoPage() {
  const kpis = useAnalyticsQuery('kpis');
  const projetos = useAnalyticsQuery('projetos_risco');
  const [scores, setScores] = useState<Score[]>([]);
  const [scoreDisponivel, setScoreDisponivel] = useState(false);
  useEffect(() => { fetch('/api/score-estouro').then(r => r.json() as Promise<unknown>).then(valor => { const r = respostaScore(valor); setScoreDisponivel(r.disponivel); setScores(r.linhas); }).catch(() => setScoreDisponivel(false)); }, []);
  if (kpis.loading || projetos.loading) return <Carregando />;
  if (kpis.error || projetos.error) return <Erro mensagem={String(kpis.error ?? projetos.error)} />;
  const resumo = kpis.data?.[0];
  const linhas = projetos.data ?? [];
  const porProjeto = new Map(scores.map(s => [s.projeto_id, s]));
  const altoRisco = scoreDisponivel ? scores.filter(s => s.faixa_risco?.toLowerCase() === 'alto').length.toString() : '—';
  return <div className="space-y-6">
    <div><h2 className="text-2xl font-semibold tracking-tight">Projetos em risco</h2><p className="text-sm text-muted-foreground">Priorize desvios de prazo, custo e capacidade.</p></div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Kpi titulo="Projetos em risco" valor={inteiro(resumo?.projetos_em_risco)} /><Kpi titulo="Estouro previsto" valor={moeda(resumo?.estouro_previsto)} /><Kpi titulo="Carteira" valor={moeda(resumo?.carteira)} /><Kpi titulo="Alto risco em 30 dias" valor={altoRisco} /></div>
    {!scoreDisponivel && <Alert><AlertDescription>O modelo de risco em 30 dias ainda não está disponível. Os demais indicadores seguem operacionais.</AlertDescription></Alert>}
    <Card><CardHeader><CardTitle>Fila de atuação</CardTitle></CardHeader><CardContent className="overflow-x-auto p-0">{linhas.length === 0 ? <Vazio mensagem="Não há projetos para acompanhar." /> : <Table><TableHeader><TableRow><TableHead>Projeto</TableHead><TableHead>Situação</TableHead><TableHead>SPI / CPI</TableHead><TableHead>Faróis</TableHead><TableHead>Estouro</TableHead><TableHead>Atraso</TableHead><TableHead>Causa principal</TableHead><TableHead>Probabilidade 30d</TableHead></TableRow></TableHeader><TableBody>{linhas.map(p => { const s = porProjeto.get(p.projeto_id); return <TableRow key={p.projeto_id}><TableCell><div className="font-medium">{p.projeto_id} · {p.projeto}</div><div className="text-xs text-muted-foreground">{p.cliente}</div></TableCell><TableCell><Badge className={classeSituacao(p.situacao)}>{p.situacao}</Badge></TableCell><TableCell className="tabular-nums">{indice(p.spi)} / {indice(p.cpi)}</TableCell><TableCell>{p.farol_do_gerente}{p.melancia ? ' 🍉' : ''} / {p.farol_calculado}</TableCell><TableCell className="tabular-nums">{moeda(p.estouro_previsto)}</TableCell><TableCell>{inteiro(p.atraso_projetado_dias)} dias</TableCell><TableCell>{p.causa_principal}</TableCell><TableCell>{s?.prob_estouro_30d == null ? '—' : `${percentual(s.prob_estouro_30d)} · ${s.faixa_risco ?? '—'}`}</TableCell></TableRow>; })}</TableBody></Table>}</CardContent></Card>
    <Fonte />
  </div>;
}

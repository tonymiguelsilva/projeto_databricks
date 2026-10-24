import { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Input, Label, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, useAnalyticsQuery } from '@databricks/appkit-ui/react';
import { Carregando, Erro, Fonte, Vazio } from '../components/Estados';
import { calcularSimulacao, indice, inteiro, moeda, percentual } from '../lib/formatos';

function Resultado({ titulo, valor }: { titulo: string; valor: string }) { return <div className="rounded-lg border bg-muted/20 p-4"><p className="text-xs text-muted-foreground">{titulo}</p><p className="mt-1 text-xl font-semibold tabular-nums">{valor}</p></div>; }

export function SimuladorPage() {
  const pessoas = useAnalyticsQuery('pessoas_ociosas');
  const projetos = useAnalyticsQuery('projetos_risco');
  const [pessoaId, setPessoaId] = useState('COL0017');
  const [projetoId, setProjetoId] = useState('PRJ-011');
  const [onboarding, setOnboarding] = useState(40);
  const destinos = useMemo(() => (projetos.data ?? []).filter(p => ['atenção', 'crítico'].includes(p.situacao)), [projetos.data]);
  if (pessoas.loading || projetos.loading) return <Carregando />;
  if (pessoas.error || projetos.error) return <Erro mensagem={String(pessoas.error ?? projetos.error)} />;
  if (!pessoas.data?.length || !destinos.length) return <Vazio mensagem="Não há pessoas ociosas ou projetos de destino elegíveis." />;
  const pessoa = pessoas.data.find(p => p.colaborador_id === pessoaId) ?? pessoas.data[0];
  const ordenados = [...destinos].sort((a, b) => pessoa.papel.toLowerCase().includes('sre') ? b.dias_falta_sre - a.dias_falta_sre : 0);
  const projeto = ordenados.find(p => p.projeto_id === projetoId) ?? ordenados[0];
  const impacto = pessoa.papel.toLowerCase().includes('sre') ? projeto.dias_falta_sre : projeto.dias_rotatividade;
  const r = calcularSimulacao(Number(pessoa.horas_paradas_semana), Number(pessoa.custo_ocioso_semana), Number(pessoa.custo_hora), Number(impacto), onboarding);
  return <div className="space-y-6">
    <div><h2 className="text-2xl font-semibold tracking-tight">Simulador de realocação</h2><p className="text-sm text-muted-foreground">Estime o efeito operacional e financeiro antes da decisão.</p></div>
    <Card><CardHeader><CardTitle>Cenário</CardTitle></CardHeader><CardContent className="grid gap-5 md:grid-cols-3"><div className="space-y-2"><Label htmlFor="pessoa">Pessoa disponível</Label><Select value={pessoa.colaborador_id} onValueChange={setPessoaId}><SelectTrigger id="pessoa"><SelectValue /></SelectTrigger><SelectContent>{pessoas.data.map(p => <SelectItem key={`${p.colaborador_id}-${p.projeto_origem}`} value={p.colaborador_id}>{p.nome} · {p.papel} · {percentual(p.utilizacao_media)}</SelectItem>)}</SelectContent></Select></div><div className="space-y-2"><Label htmlFor="destino">Projeto destino</Label><Select value={projeto.projeto_id} onValueChange={setProjetoId}><SelectTrigger id="destino"><SelectValue /></SelectTrigger><SelectContent>{ordenados.map(p => <SelectItem key={p.projeto_id} value={p.projeto_id}>{p.projeto_id} · {p.projeto} · {p.situacao}</SelectItem>)}</SelectContent></Select></div><div className="space-y-2"><Label htmlFor="onboarding">Onboarding (horas)</Label><Input id="onboarding" type="number" min="0" value={onboarding} onChange={e => setOnboarding(Number(e.target.value))} /></div></CardContent></Card>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5"><Resultado titulo="Horas disponíveis/mês" valor={`${indice(r.horasMensais)}h`} /><Resultado titulo="Ociosidade evitada/mês" valor={moeda(r.ociosidadeEvitada)} /><Resultado titulo="Dias recuperados" valor={`${inteiro(r.diasRecuperados)} dias`} /><Resultado titulo="Mobilização" valor={moeda(r.mobilizacao)} /><Resultado titulo="Saldo mensal" valor={moeda(r.saldo)} /></div>
    <Card><CardHeader><CardTitle>Leitura do cenário</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><p><strong>{pessoa.nome}</strong> está com {percentual(pessoa.utilizacao_media)} de utilização e média de {indice(pessoa.horas_paradas_semana)} horas ociosas por semana no {pessoa.projeto_origem}. A alocação sugerida é para <strong>{projeto.projeto_id} · {projeto.projeto}</strong>.</p><details className="rounded-md border p-4"><summary className="cursor-pointer font-medium">Premissas e fórmulas</summary><ul className="mt-3 list-disc space-y-1 pl-5 text-muted-foreground"><li>Horas mensais = média semanal × 4.</li><li>Ociosidade evitada = custo ocioso semanal × 4.</li><li>Dias recuperados = impacto dos últimos 90 dias ÷ 90 × 30.</li><li>Mobilização = horas de onboarding × custo/hora.</li><li>Saldo = ociosidade evitada − mobilização.</li></ul></details></CardContent></Card>
    <Fonte />
  </div>;
}

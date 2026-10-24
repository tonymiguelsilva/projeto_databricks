import { useEffect, useState } from 'react';
import { Badge, Card, CardContent, CardDescription, CardHeader, CardTitle, GenieChat, Skeleton } from '@databricks/appkit-ui/react';

type Identidade = { email: string | null; user: string | null };

function identidade(valor: unknown): Identidade | null {
  if (typeof valor !== 'object' || valor === null) return null;
  const item = valor as { email?: unknown; user?: unknown };
  return {
    email: typeof item.email === 'string' ? item.email : null,
    user: typeof item.user === 'string' ? item.user : null,
  };
}

export function PerguntarPage() {
  const [usuario, setUsuario] = useState<Identidade | null>(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    fetch('/api/whoami')
      .then((resposta) => resposta.json() as Promise<unknown>)
      .then((valor) => setUsuario(identidade(valor)))
      .catch(() => setUsuario(null))
      .finally(() => setCarregando(false));
  }, []);

  return <div className="space-y-6">
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div><h2 className="text-2xl font-semibold tracking-tight">Perguntar</h2><p className="text-sm text-muted-foreground">Converse com o Farol · Diretoria usando linguagem natural.</p></div>
      {carregando ? <Skeleton className="h-6 w-44" /> : <Badge variant="secondary">{usuario?.email ?? usuario?.user ?? 'Usuário autenticado'}</Badge>}
    </div>
    <Card>
      <CardHeader><CardTitle>Assistente executivo</CardTitle><CardDescription>As consultas são executadas em seu nome e respeitam suas permissões no Databricks.</CardDescription></CardHeader>
      <CardContent><div className="h-[70vh] min-h-[560px]"><GenieChat alias="default" /></div></CardContent>
    </Card>
    <p className="text-xs text-muted-foreground">Resposta gerada por IA a partir dos dados do Projeto Farol. Revise o SQL exibido pelo Genie antes de tomar decisões.</p>
  </div>;
}

import { Alert, AlertDescription, AlertTitle, Empty, EmptyDescription, EmptyHeader, EmptyTitle, Skeleton } from '@databricks/appkit-ui/react';

export function Carregando() { return <div className="space-y-3" aria-label="Carregando"><Skeleton className="h-24 w-full" /><Skeleton className="h-64 w-full" /></div>; }
export function Erro({ mensagem }: { mensagem: string }) { return <Alert variant="destructive"><AlertTitle>Não foi possível carregar os dados</AlertTitle><AlertDescription>{mensagem}</AlertDescription></Alert>; }
export function Vazio({ mensagem }: { mensagem: string }) { return <Empty><EmptyHeader><EmptyTitle>Nenhum resultado</EmptyTitle><EmptyDescription>{mensagem}</EmptyDescription></EmptyHeader></Empty>; }
export function Fonte() { return <p className="text-xs text-muted-foreground">Fonte: Unity Catalog · atualização conforme a última execução do Projeto Farol.</p>; }

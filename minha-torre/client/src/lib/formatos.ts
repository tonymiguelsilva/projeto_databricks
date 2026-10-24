export const numero = (valor: unknown) => Number(valor ?? 0);
export const moeda = (valor: unknown) => numero(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
export const indice = (valor: unknown) => numero(valor).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const percentual = (valor: unknown) => numero(valor).toLocaleString('pt-BR', { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 });
export const inteiro = (valor: unknown) => Math.round(numero(valor)).toLocaleString('pt-BR');

export function classeSituacao(situacao: string) {
  if (situacao === 'crítico') return 'bg-destructive/10 text-destructive';
  if (situacao === 'atenção') return 'bg-warning/20 text-warning-foreground';
  return 'bg-success/10 text-success';
}

export function calcularSimulacao(horasSemanais: number, custoOciosoSemanal: number, custoHora: number, impacto90d: number, onboarding: number) {
  const horasMensais = horasSemanais * 4;
  const ociosidadeEvitada = custoOciosoSemanal * 4;
  const diasRecuperados = impacto90d / 90 * 30;
  const mobilizacao = onboarding * custoHora;
  return { horasMensais, ociosidadeEvitada, diasRecuperados, mobilizacao, saldo: ociosidadeEvitada - mobilizacao };
}

import { getExecutionContext } from '@databricks/appkit';
import type { Application } from 'express';

interface AppKitComServidor {
  server: { extend(fn: (app: Application) => void): void };
}

const SQL = `
  SELECT projeto_id, prob_estouro_30d, ranking, faixa_risco
  FROM lakehouse_vertice.gold.score_estouro_30d
  WHERE data_referencia = (
    SELECT MAX(data_referencia) FROM lakehouse_vertice.gold.score_estouro_30d
  )`;

export function registrarRotaScore(appkit: AppKitComServidor) {
  appkit.server.extend((app) => {
    app.get('/api/score-estouro', async (_req, res) => {
      try {
        const contexto = getExecutionContext();
        const warehouseId = (await contexto.warehouseId) ?? process.env.DATABRICKS_WAREHOUSE_ID ?? '';
        const resultado = await contexto.client.statementExecution.executeStatement({
          warehouse_id: warehouseId,
          statement: SQL,
          wait_timeout: '30s',
        });
        if (resultado.status?.state !== 'SUCCEEDED') {
          res.json({ disponivel: false, motivo: resultado.status?.error?.message ?? resultado.status?.state, linhas: [] });
          return;
        }
        const colunas = (resultado.manifest?.schema?.columns ?? []).map((coluna) => coluna.name ?? '');
        const linhas = (resultado.result?.data_array ?? []).map((linha) =>
          Object.fromEntries(colunas.map((coluna, indice) => [coluna, linha[indice] ?? null])),
        );
        res.json({ disponivel: linhas.length > 0, linhas });
      } catch (erro) {
        res.json({ disponivel: false, motivo: erro instanceof Error ? erro.message : String(erro), linhas: [] });
      }
    });
  });
}

import type { Application } from 'express';

interface AppKitComServidor {
  server: { extend(fn: (app: Application) => void): void };
}

export function registrarRotaIdentidade(appkit: AppKitComServidor) {
  appkit.server.extend((app) => {
    app.get('/api/whoami', (req, res) => {
      res.json({
        email: req.header('x-forwarded-email') ?? null,
        user: req.header('x-forwarded-user') ?? null,
      });
    });
  });
}

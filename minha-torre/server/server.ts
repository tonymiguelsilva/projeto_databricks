import { createApp, analytics, genie, server } from '@databricks/appkit';
import { registrarRotaScore } from './routes/score';
import { registrarRotaIdentidade } from './routes/identidade';

createApp({
  plugins: [
    analytics(),
    genie(),
    server(),
  ],
  cache: { enabled: false },
  onPluginsReady(appkit) {
    registrarRotaScore(appkit);
    registrarRotaIdentidade(appkit);
  },
}).catch(console.error);

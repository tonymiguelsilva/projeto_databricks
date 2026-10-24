import { createApp, analytics, server } from '@databricks/appkit';
import { registrarRotaScore } from './routes/score';

createApp({
  plugins: [
    analytics(),
    server(),
  ],
  cache: { enabled: false },
  onPluginsReady(appkit) {
    registrarRotaScore(appkit);
  },
}).catch(console.error);

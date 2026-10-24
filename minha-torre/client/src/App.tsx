import { createBrowserRouter, NavLink, Outlet, RouterProvider } from 'react-router';
import { useState } from 'react';
import { Button, Sheet, SheetContent, SheetHeader, SheetTitle, useIsMobile } from '@databricks/appkit-ui/react';
import { Menu, MessageCircle, Radar, Users } from 'lucide-react';
import { ProjetosRiscoPage } from './pages/ProjetosRiscoPage';
import { SimuladorPage } from './pages/SimuladorPage';
import { PerguntarPage } from './pages/PerguntarPage';

const link = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`;

function Navegacao({ fechar }: { fechar?: () => void }) {
  return <nav className="flex flex-col gap-1 md:flex-row">
    <NavLink to="/" end className={link} onClick={fechar}><Radar className="h-4 w-4" />Projetos em risco</NavLink>
    <NavLink to="/simulador" className={link} onClick={fechar}><Users className="h-4 w-4" />Simulador</NavLink>
    <NavLink to="/perguntar" className={link} onClick={fechar}><MessageCircle className="h-4 w-4" />Perguntar</NavLink>
  </nav>;
}

function Layout() {
  const mobile = useIsMobile();
  const [aberto, setAberto] = useState(false);
  return <div className="min-h-screen bg-background text-foreground">
    <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex max-w-[1600px] items-center gap-6 px-4 py-3 md:px-6">
        <div><h1 className="text-lg font-semibold">Projeto Farol</h1><p className="text-xs text-muted-foreground">Torre de controle do portfólio</p></div>
        <div className="hidden md:block"><Navegacao /></div>
        <div className="ml-auto md:hidden"><Sheet open={aberto && mobile} onOpenChange={setAberto}><Button variant="ghost" size="icon" onClick={() => setAberto(true)} aria-label="Abrir navegação"><Menu /></Button><SheetContent side="left"><SheetHeader><SheetTitle>Projeto Farol</SheetTitle></SheetHeader><div className="mt-6"><Navegacao fechar={() => setAberto(false)} /></div></SheetContent></Sheet></div>
      </div>
    </header>
    <main className="mx-auto max-w-[1600px] p-4 md:p-6"><Outlet /></main>
  </div>;
}

const router = createBrowserRouter([{ element: <Layout />, children: [
  { path: '/', element: <ProjetosRiscoPage /> },
  { path: '/simulador', element: <SimuladorPage /> },
  { path: '/perguntar', element: <PerguntarPage /> },
]}]);

export default function App() { return <RouterProvider router={router} />; }

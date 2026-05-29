import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import type { Page } from "../../App";
import { Sidebar } from "./Sidebar";

interface LayoutProps {
  children: ReactNode;
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Layout({ children, activePage, onNavigate }: LayoutProps) {
  return (
    // Fundo escuro (Dark Mode) e display flex para alinhar a sidebar
    <div className="min-h-screen bg-[#0A0A0A] text-zinc-200 flex font-sans">

      {/* 🟢 Nova Barra Lateral Escura */}
      <Sidebar />

      {/* Conteúdo Principal empurrado para a direita (ml-64 = espaço da sidebar) */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">

        {/* Menu interno do seu projeto (Dashboard, Criar, etc) */}
        <header className="border-b border-white/5 bg-[#0A0A0A]/80 backdrop-blur-md sticky top-0 z-40">
          <div className="max-w-6xl mx-auto px-8">
             <Navigation activePage={activePage} onNavigate={onNavigate} />
          </div>
        </header>

        {/* Telas principais renderezadas aqui */}
        <main className="flex-1 max-w-6xl w-full mx-auto px-8 py-10">
          {children}
        </main>
      </div>
    </div>
  );
}
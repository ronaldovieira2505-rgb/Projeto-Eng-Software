import type { ReactNode } from "react";
import { Navigation } from "./Navigation";
import type { Page } from "../../App";
import { TopBar } from "./TopBar";

interface LayoutProps {
  children: ReactNode;
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Layout({ children, activePage, onNavigate }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Nova TopBar Integrada com o Ecossistema */}
      <TopBar />

      {/* Navegação interna do SEU módulo (Abas de Dashboard, Criar, etc) */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          <Navigation activePage={activePage} onNavigate={onNavigate} />
        </div>
      </div>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>

      {/* Footer */}
      <footer className="text-center py-6 text-xs text-gray-400">
        Powered by AI • Economize tempo na criação de apresentações técnicas
      </footer>
    </div>
  );
} // 🟢 FALTAVA ESSA CHAVE AQUI
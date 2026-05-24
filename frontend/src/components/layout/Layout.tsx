import type { ReactNode } from "react";
import { Navigation } from "./Navigation";
import type { Page } from "../../App";

interface LayoutProps {
  children: ReactNode;
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Layout({ children, activePage, onNavigate }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          {/* Logo */}
          <div className="flex items-center gap-3 pt-5 pb-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="white" className="h-5 w-5">
                <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900 leading-tight">
                Módulo de Apresentações
              </h1>
              <p className="text-xs text-gray-500">Crie apresentações inteligentes com IA</p>
            </div>
          </div>

          {/* Navigation tabs */}
          <Navigation activePage={activePage} onNavigate={onNavigate} />
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>

      {/* Footer */}
      <footer className="text-center py-6 text-xs text-gray-400">
        Powered by AI • Economize tempo na criação de apresentações técnicas
      </footer>
    </div>
  );
}

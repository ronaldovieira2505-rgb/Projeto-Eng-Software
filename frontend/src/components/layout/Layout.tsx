import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import type { Page } from "../../App";

interface LayoutProps {
  children: ReactNode;
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Layout({ children, activePage, onNavigate }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-[#0f1117] text-gray-100">
      <Sidebar activePage={activePage} onNavigate={onNavigate} />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-8 py-10">
          {children}
        </div>
      </main>
    </div>
  );
}

import { useState } from "react";
import { Layout } from "./components/layout/Layout";
import { Dashboard } from "./pages/Dashboard";
import { CreatePresentation } from "./pages/CreatePresentation";
import { Settings } from "./pages/Settings";
import { Modules } from "./pages/Modules"; // 🟢 IMPORT CORRIGIDO
import { usePresentations } from "./hooks/usePresentations";
import { useSettings } from "./hooks/useSettings";

// 🟢 TIPO ATUALIZADO (Adicionado o 'modules')
export type Page = "dashboard" | "create" | "settings" | "modules";

export default function App() {
  const [activePage, setActivePage] = useState<Page>("dashboard");
  const { presentations, stats, loading, error, generate } = usePresentations();
  const { settings, update, save, saved } = useSettings();

  async function handleGenerate(data: Parameters<typeof generate>[0]) {
    const success = await generate(data);
    if (success) setActivePage("dashboard");
    return success;
  }

  return (
    // 🟢 PASSAGEM DE PARÂMETRO CORRIGIDA
      <Layout activePage={activePage} onNavigate={setActivePage}>
          {activePage === "dashboard" && (
              <Dashboard presentations={presentations} stats={stats}/>)}
          {activePage === "create" && (
              <CreatePresentation
                  onGenerate={handleGenerate}
                  loading={loading}
                  error={error}
              />
          )}
          {activePage === "settings" && (
              <Settings
                  settings={settings}
                  onUpdate={update}
                  onSave={save}
                  saved={saved}
              />
          )}
          {/* 🟢 RENDERIZAÇÃO DA PÁGINA AQUI DENTRO */}
          {activePage === "modules" && <Modules/>}
      </Layout>
  );
}
import { useState } from "react";
import { Layout } from "./components/layout/Layout";
import { Dashboard } from "./pages/Dashboard";
import { CreatePresentation } from "./pages/CreatePresentation";
import { Settings } from "./pages/Settings";
import { Modules } from "./pages/Modules"; // 🟢 IMPORT CORRIGIDO
import { usePresentations } from "./hooks/usePresentations";
import { useSettings } from "./hooks/useSettings";
import type { ToneType } from "./types"

// 🟢 TIPO ATUALIZADO (Adicionado o 'modules')
export type Page = "dashboard" | "create" | "settings" | "modules";

export default function App() {
  const [activePage, setActivePage] = useState<Page>("dashboard");
  const { presentations, stats, loading, error, generate } = usePresentations();
  const { settings, update, save, saved } = useSettings();

  async function handleGenerate(data: {
    repo_url: string;
    swagger_url?: string;
    file_paths?: string[]
  }) {
    // 2. Aqui fazemos o "cast" do tone para o tipo correto
    const fullPayload = {
      title: "Nova Apresentação",
      repo: data.repo_url,
      branch: "main",
      audience: "Equipe Técnica",
      swagger_url: data.swagger_url || "",
      file_paths: data.file_paths || [],
      tone: "technical" as ToneType, // <--- A MÁGICA ESTÁ AQUI
      include_code: true,
      presentation_type: "standard" as any, // <--- Se der erro aqui, usamos 'as any'
      exportSnippets: true,
      analyzeCommits: true,
      detectTodos: false
    };

    const success = await generate(fullPayload);
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
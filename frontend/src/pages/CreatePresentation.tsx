import { useState } from "react";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Checkbox } from "../components/ui/Checkbox";
import { Button } from "../components/ui/Button";
import {
  PresentationTypeCard,
  PRESENTATION_TYPES,
} from "../components/presentation/PresentationTypeCard";
import type { PresentationType, ToneType, GenerateFromCommitsRequest } from "../types";

const AUDIENCE_OPTIONS = [
  { value: "", label: "Selecione o público" },
  { value: "tech_lead", label: "Tech Lead" },
  { value: "product_manager", label: "Product Manager" },
  { value: "stakeholders", label: "Stakeholders" },
  { value: "engineering", label: "Time de Engenharia" },
  { value: "executive", label: "Diretoria / C-Level" },
];

const TONE_OPTIONS: { value: ToneType; label: string }[] = [
  { value: "formal", label: "Profissional" },
  { value: "technical", label: "Técnico" },
  { value: "persuasive", label: "Persuasivo" },
  { value: "simplified", label: "Simplificado" },
];

interface CreatePresentationProps {
  onGenerate: (data: GenerateFromCommitsRequest) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

export function CreatePresentation({
  onGenerate,
  loading,
  error,
}: CreatePresentationProps) {
  const [title, setTitle] = useState("");
  const [selectedType, setSelectedType] = useState<PresentationType>("sprint_review");
  const [repo, setRepo] = useState("");
  const [branch, setBranch] = useState("main");
  const [audience, setAudience] = useState("");
  const [tone, setTone] = useState<ToneType>("formal");
  const [exportSnippets, setExportSnippets] = useState(true);
  const [analyzeCommits, setAnalyzeCommits] = useState(true);
  const [detectTodos, setDetectTodos] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onGenerate({
      title,
      repo,
      branch,
      audience,
      tone,
      presentation_type: selectedType,
      exportSnippets,
      analyzeCommits,
      detectTodos,
    });
  }

  return (
    <div className="max-w-3xl mx-auto">
      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-xl shadow-sm p-6 flex flex-col gap-6">
          <h2 className="text-xl font-semibold text-gray-900">Nova Apresentação</h2>

          {/* Título */}
          <Input
            label="Título da Apresentação"
            placeholder="Ex: Sprint Review - Q2 2026"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          {/* Tipo de apresentação */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">
              Tipo de Apresentação
            </label>
            <div className="grid grid-cols-2 gap-3">
              {PRESENTATION_TYPES.map((opt) => (
                <PresentationTypeCard
                  key={opt.id}
                  option={opt}
                  selected={selectedType === opt.id}
                  onSelect={setSelectedType}
                />
              ))}
            </div>
          </div>

          {/* Repositório */}
          <Input
            label="URL do Repositório"
            placeholder="https://github.com/usuario/repositorio.git"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            required
            icon={
              <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
                <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
              </svg>
            }
          />

          {/* Branch */}
          <Input
            label="Branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
          />

          {/* Público-Alvo + Tom de Voz */}
          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Público-Alvo"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              options={AUDIENCE_OPTIONS}
            />
            <Select
              label="Tom de Voz"
              value={tone}
              onChange={(e) => setTone(e.target.value as ToneType)}
              options={TONE_OPTIONS}
            />
          </div>

          {/* Recursos da IA */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-700">Recursos da IA</label>
            <div className="flex flex-col gap-2">
              <Checkbox
                label="Exportar snippets de código formatados"
                description="Inclui blocos de código com syntax highlight"
                checked={exportSnippets}
                onChange={setExportSnippets}
              />
              <Checkbox
                label="Analisar commits com LLM"
                description="Transforma commits em artefatos para apresentação"
                checked={analyzeCommits}
                onChange={setAnalyzeCommits}
              />
              <Checkbox
                label="Detectar TODOs no código"
                description="Gera lista de pendências técnicas automaticamente"
                checked={detectTodos}
                onChange={setDetectTodos}
              />
            </div>
          </div>

          {/* Error */}
          {error && (
            <p className="text-sm text-red-600 bg-red-50 p-3 rounded-lg">{error}</p>
          )}

          {/* Submit */}
          <Button type="submit" loading={loading} className="w-full text-base py-4">
            <svg viewBox="0 0 24 24" fill="white" className="h-4 w-4">
              <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z" />
            </svg>
            Gerar Apresentação com IA
          </Button>
        </div>
      </form>
    </div>
  );
}

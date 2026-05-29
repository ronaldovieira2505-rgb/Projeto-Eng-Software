import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Checkbox } from "../components/ui/Checkbox";
import { Button } from "../components/ui/Button";
import type { AppSettings, ToneType } from "../types";

const TONE_OPTIONS: { value: ToneType; label: string }[] = [
  { value: "formal", label: "Profissional" },
  { value: "technical", label: "Técnico" },
  { value: "persuasive", label: "Persuasivo" },
  { value: "simplified", label: "Simplificado" },
];

interface SettingsProps {
  settings: AppSettings;
  onUpdate: (partial: Partial<AppSettings>) => void;
  onSave: () => void;
  saved: boolean;
}

export function Settings({ settings, onUpdate, onSave, saved }: SettingsProps) {
  return (
    <div className="max-w-2xl mx-auto flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

      <div>
        <h2 className="text-3xl font-light text-white tracking-tight">
          Configurações do <span className="font-semibold text-cyan-400">Módulo</span>
        </h2>
        <p className="text-zinc-400 mt-2 text-lg font-light">
          Ajuste as suas credenciais e preferências de geração de IA.
        </p>
      </div>

      {/* Integrações e API Keys */}
      <section className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-[2rem] p-8 shadow-2xl flex flex-col gap-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
            <svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2" className="h-5 w-5">
              <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" />
              <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white">Integrações e API Keys</h2>
        </div>

        <Input
          label="Token de Acesso do GitHub"
          type="password"
          placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
          value={settings.githubToken}
          onChange={(e) => onUpdate({ githubToken: e.target.value })}
          helper="Necessário para acessar repositórios privados"
          icon={
            <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
              <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.335-1.755-1.335-1.755-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
            </svg>
          }
        />

        <Input
          label="Chave da API OpenAI"
          type="password"
          placeholder="sk-xxxxxxxxxxxxxxxxxxxx"
          value={settings.openaiApiKey}
          onChange={(e) => onUpdate({ openaiApiKey: e.target.value })}
          helper="Para análise de commits e geração de conteúdo"
          icon={
            <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4">
              <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z" />
            </svg>
          }
        />
      </section>

      {/* Preferências de Geração */}
      <section className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-[2rem] p-8 shadow-2xl flex flex-col gap-6">
        <h2 className="text-xl font-semibold text-white mb-2">Preferências de Geração</h2>

        <Select
          label="Tom de Voz Padrão"
          value={settings.defaultTone}
          onChange={(e) => onUpdate({ defaultTone: e.target.value as ToneType })}
          options={TONE_OPTIONS}
        />

        <Checkbox
          label="Analisar commits automaticamente"
          description="Usar LLM para interpretar commits ao criar apresentações"
          checked={settings.autoAnalyzeCommits}
          onChange={(v) => onUpdate({ autoAnalyzeCommits: v })}
        />

        <Checkbox
          label="Incluir snippets de código"
          description="Adicionar blocos de código formatados por padrão"
          checked={settings.includeCodeSnippets}
          onChange={(v) => onUpdate({ includeCodeSnippets: v })}
        />
      </section>

      {/* Notificações */}
      <section className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-[2rem] p-8 shadow-2xl flex flex-col gap-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
            <svg viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" className="h-5 w-5">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white">Notificações</h2>
        </div>

        <Checkbox
          label="Notificações por e-mail"
          description="Receber alertas quando apresentações forem concluídas"
          checked={settings.emailNotifications}
          onChange={(v) => onUpdate({ emailNotifications: v })}
        />

        <Input
          label="Webhook do Slack (opcional)"
          type="url"
          placeholder="https://hooks.slack.com/services/..."
          value={settings.slackWebhook}
          onChange={(e) => onUpdate({ slackWebhook: e.target.value })}
          helper="Enviar notificações para um canal do Slack"
        />
      </section>

      {/* Save Button */}
      <div className="flex justify-end mt-4">
        <Button
          onClick={onSave}
          className={`px-8 py-3 rounded-xl font-semibold transition-all ${saved ? "bg-emerald-500 hover:bg-emerald-600 text-black shadow-[0_0_15px_rgba(16,185,129,0.4)]" : "bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)]"}`}
        >
          {saved ? (
            <span className="flex items-center gap-2">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="h-5 w-5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Salvo com Sucesso!
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
                <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" />
                <polyline points="17 21 17 13 7 13 7 21" />
                <polyline points="7 3 7 8 15 8" />
              </svg>
              Salvar Configurações
            </span>
          )}
        </Button>
      </div>
    </div>
  );
}
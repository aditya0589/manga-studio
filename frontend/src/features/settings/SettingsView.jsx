import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { settingsApi } from '../../api/settings';
import { 
  Settings as SettingsIcon, 
  Cpu, 
  Sparkles, 
  HardDrive, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  ShieldCheck,
  Zap
} from 'lucide-react';

export default function SettingsView() {
  const { data: providerStatus, isLoading: isStatusLoading } = useQuery({
    queryKey: ['settingsProviders'],
    queryFn: () => settingsApi.getProviders(),
  });

  const { data: modelsData } = useQuery({
    queryKey: ['settingsModels'],
    queryFn: () => settingsApi.getModels(),
  });

  const { data: usage = [] } = useQuery({
    queryKey: ['settingsUsage'],
    queryFn: () => settingsApi.getUsage(),
  });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white font-['Plus_Jakarta_Sans'] flex items-center gap-2.5">
          <SettingsIcon className="w-6 h-6 text-violet-400" />
          <span>Studio Settings & AI Providers</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Inspect cloud provider credentials, generation limits, and active AI models
        </p>
      </div>

      <div className="space-y-6">
        {/* Status Alert Banner */}
        {providerStatus && (
          <div className={`p-4 rounded-xl border flex items-start gap-3 ${
            providerStatus.is_mock_mode
              ? 'bg-amber-950/30 border-amber-800/50 text-amber-300'
              : 'bg-emerald-950/30 border-emerald-800/50 text-emerald-300'
          }`}>
            {providerStatus.is_mock_mode ? (
              <Info className="w-5 h-5 shrink-0 text-amber-400 mt-0.5" />
            ) : (
              <ShieldCheck className="w-5 h-5 shrink-0 text-emerald-400 mt-0.5" />
            )}
            <div>
              <h4 className="font-bold text-sm">
                {providerStatus.is_mock_mode ? "Limited Mode Active (Safe Studio Mock Engine)" : "Cloud AI Providers Connected"}
              </h4>
              <p className="text-xs mt-1 leading-relaxed opacity-90">
                {providerStatus.is_mock_mode
                  ? "Real cloud credentials (OPENROUTER_API_KEY, CLOUDFLARE_API_TOKEN) are not currently supplied in your .env. The studio is operating with local high-contrast manga mock generation so you can test all agents, panel editing, and PDF exporting without burning API credits."
                  : "Both OpenRouter and Cloudflare Workers AI are authenticated and ready for live cloud inference."
                }
              </p>
            </div>
          </div>
        )}

        {/* Providers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* OpenRouter LLM Card */}
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-violet-950 border border-violet-800/40 flex items-center justify-center text-violet-400">
                  <Cpu className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-sm text-white">LLM Provider (OpenRouter)</h3>
              </div>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                providerStatus?.openrouter_configured ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
              }`}>
                {providerStatus?.openrouter_configured ? 'Configured' : 'Offline / Mock'}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#1d2230]">
                <span className="text-slate-400">Primary Model:</span>
                <span className="font-mono text-slate-200">{providerStatus?.openrouter_model || "anthropic/claude-3.5-sonnet"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1d2230]">
                <span className="text-slate-400">Fallback Free Model:</span>
                <span className="font-mono text-slate-200">{providerStatus?.openrouter_fallback_model || "meta-llama/llama-3.3-70b-instruct:free"}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">API Key Mask:</span>
                <span className="font-mono text-slate-500">
                  {providerStatus?.openrouter_configured ? "sk-or-••••••••••••" : "Not Provided"}
                </span>
              </div>
            </div>
          </div>

          {/* Cloudflare Workers AI Card */}
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-violet-950 border border-violet-800/40 flex items-center justify-center text-violet-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-sm text-white">Image Provider (Cloudflare)</h3>
              </div>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                providerStatus?.cloudflare_configured ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
              }`}>
                {providerStatus?.cloudflare_configured ? 'Configured' : 'Offline / Mock'}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#1d2230]">
                <span className="text-slate-400">Image Model:</span>
                <span className="font-mono text-slate-200">{providerStatus?.cloudflare_image_model || "@cf/black-forest-labs/flux-1-schnell"}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#1d2230]">
                <span className="text-slate-400">Architecture:</span>
                <span className="text-slate-200">Text-to-Image (Flux 1 Schnell REST)</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-400">API Token:</span>
                <span className="font-mono text-slate-500">
                  {providerStatus?.cloudflare_configured ? "cf-••••••••••••" : "Not Provided"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Available Models Reference */}
        {modelsData && (
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] shadow-lg space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-violet-400" />
              <span>Supported Studio Models</span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Language Models (LLM)</h4>
                <div className="space-y-1.5">
                  {modelsData.llm_models?.map((m) => (
                    <div key={m.id} className="p-2.5 rounded-xl bg-[#090b10] border border-[#222736] flex justify-between items-center">
                      <span className="text-slate-200 font-medium">{m.name}</span>
                      <span className="text-[10px] text-slate-500 font-mono">{m.context.toLocaleString()} tokens</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-slate-300 mb-2">Image Models</h4>
                <div className="space-y-1.5">
                  {modelsData.image_models?.map((m) => (
                    <div key={m.id} className="p-2.5 rounded-xl bg-[#090b10] border border-[#222736] flex justify-between items-center">
                      <span className="text-slate-200 font-medium">{m.name}</span>
                      <span className="text-[10px] text-violet-400 font-semibold">{m.type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Storage and Database Details */}
        <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] shadow-lg space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-violet-400" />
            <span>Infrastructure & Storage Engine</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-[#090b10] border border-[#222736]">
              <span className="text-slate-500 block mb-1">Database Mode</span>
              <span className="font-semibold text-slate-200 capitalize">{providerStatus?.database_mode || 'SQLite'} (Async SQLAlchemy 2.0)</span>
            </div>
            <div className="p-3 rounded-xl bg-[#090b10] border border-[#222736]">
              <span className="text-slate-500 block mb-1">Asset Storage</span>
              <span className="font-semibold text-slate-200 capitalize">{providerStatus?.storage_backend || 'Local'} Filesystem Adapter</span>
            </div>
            <div className="p-3 rounded-xl bg-[#090b10] border border-[#222736]">
              <span className="text-slate-500 block mb-1">Publishing Exporter</span>
              <span className="font-semibold text-slate-200">ReportLab Tankobon B5 / A4 Engine</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  Layers, 
  Cpu, 
  Palette, 
  FileText, 
  Download, 
  ArrowRight, 
  CheckCircle2, 
  ShieldCheck,
  Zap,
  BookOpen
} from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0b0e] text-slate-100 flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-32 px-4 sm:px-6 max-w-7xl mx-auto w-full">
        {/* Subtle background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-violet-600/15 rounded-full blur-[140px] pointer-events-none" />
        
        <div className="relative text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-violet-950/60 border border-violet-800/50 text-violet-300 text-xs font-semibold shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-violet-400" />
            <span>Next-Generation Agentic AI Manga Studio</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white font-['Plus_Jakarta_Sans'] leading-[1.15]">
            Transform Stories into <span className="bg-gradient-to-r from-violet-400 via-purple-300 to-indigo-400 bg-clip-text text-transparent">Illustrated Manga</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 leading-relaxed max-w-2xl mx-auto">
            Upload your manuscripts or brainstorm original ideas. A multi-agent LangGraph workflow handles story architecture, character consistency, dynamic panel composition, dialogue overlays, and print-ready PDF publishing.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/register"
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-7 py-3.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-sm shadow-xl shadow-violet-900/30 hover:shadow-violet-900/50 transition-all group"
            >
              <span>Launch Studio</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#141722] hover:bg-[#1c2030] text-slate-200 border border-[#272b3c] font-semibold text-sm transition-colors"
            >
              Sign In to Workspace
            </Link>
          </div>

          <div className="pt-8 flex items-center justify-center gap-8 text-xs text-slate-500 font-medium">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Full LangGraph Multi-Agent Engine</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Cloudflare Workers AI (Flux Schnell)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Interactive Dialogue & Panel Editor</span>
            </div>
          </div>
        </div>

        {/* Visual Studio Preview Banner */}
        <div className="mt-16 relative rounded-2xl border border-[#252a3a] bg-[#10121a] p-4 sm:p-6 shadow-2xl overflow-hidden max-w-5xl mx-auto">
          <div className="flex items-center justify-between pb-4 border-b border-[#202534] text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-rose-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              <span className="ml-2 font-mono text-slate-300">chapter_01_awakening.manga</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-violet-950 text-violet-300 font-semibold border border-violet-800/40 text-[11px]">
                Right-to-Left (Manga Grid)
              </span>
            </div>
          </div>

          {/* Grid Preview Panels */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
            <div className="aspect-[4/3] rounded-xl bg-[#090b10] border-2 border-slate-700/60 p-4 relative flex flex-col justify-between overflow-hidden shadow-inner group">
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />
              <div className="relative z-10 self-end narration-box">
                FLOATING IRON DISTRICT. MIDNIGHT.
              </div>
              <div className="relative z-10 self-start speech-bubble max-w-[200px]">
                "Master... I won't let your legacy turn to ashes."
              </div>
              <div className="relative z-10 self-end sound-effect-tag text-purple-400 text-lg">
                ROOOAAAR!
              </div>
            </div>

            <div className="aspect-[4/3] rounded-xl bg-[#090b10] border-2 border-slate-700/60 p-4 relative flex flex-col justify-between overflow-hidden shadow-inner group">
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />
              <div className="relative z-10 self-start thought-bubble max-w-[200px]">
                "The spirit blade is resonating with my pulse..."
              </div>
              <div className="relative z-10 self-end speech-bubble max-w-[220px]">
                "KURO, CONSUME THE SHADOWS!"
              </div>
              <div className="relative z-10 self-center sound-effect-tag text-violet-300 text-2xl tracking-widest">
                ZKKKKSHHH!
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 9-Agent Workflow Section */}
      <section className="py-16 px-4 sm:px-6 max-w-7xl mx-auto w-full border-t border-[#1d2230]">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white font-['Plus_Jakarta_Sans']">
            Autonomous 9-Agent Production Pipeline
          </h2>
          <p className="text-sm text-slate-400 mt-2">
            Every chapter passes through specialized AI agents orchestrated with LangGraph state machines, conditional quality gates, and approval interrupts.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl bg-[#121520] border border-[#212638] hover:border-violet-600/40 transition-colors space-y-3">
            <div className="w-10 h-10 rounded-lg bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base">Story Ingestion & Canon Bible</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Extracts characters, factions, and rules from your uploaded manuscripts. Maintains a structured project canon so characters don't change appearance or history unexpectedly.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-[#121520] border border-[#212638] hover:border-violet-600/40 transition-colors space-y-3">
            <div className="w-10 h-10 rounded-lg bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base">Manga Director & Dialogue</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Transforms scenes into shot-by-shot panel scripts with dynamic camera angles, lighting, onomatopoeia sound effects, and speech bubbles separated from image generation prompts.
            </p>
          </div>

          <div className="p-6 rounded-xl bg-[#121520] border border-[#212638] hover:border-violet-600/40 transition-colors space-y-3">
            <div className="w-10 h-10 rounded-lg bg-violet-950/60 border border-violet-800/40 flex items-center justify-center text-violet-400">
              <Download className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-white text-base">Visual Editor & PDF Publishing</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Edit speech bubbles and reorder panels in the interactive editor. Export high-resolution B5/A4 manga PDFs with custom covers, page numbering, and right-to-left reading flow.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#1d2230] py-8 px-4 text-center text-xs text-slate-500">
        <p>AI Manga Studio &copy; {new Date().getFullYear()} &mdash; Autonomous Agentic Manga Creation Platform.</p>
        <p className="mt-1 text-[11px] text-slate-600">Built with React JS, JSX, Vite, Tailwind CSS, FastAPI, LangGraph, and ReportLab.</p>
      </footer>
    </div>
  );
}

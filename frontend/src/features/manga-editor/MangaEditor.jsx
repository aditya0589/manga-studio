import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../../api/projects';
import { mangaApi } from '../../api/manga';
import { useStudioStore } from '../../stores/studioStore';
import { 
  Palette, 
  Layers, 
  RefreshCw, 
  MessageSquare, 
  Sparkles, 
  Plus, 
  Check, 
  Download, 
  ChevronLeft, 
  ChevronRight, 
  Loader2, 
  Compass, 
  Volume2, 
  BookMarked,
  Sliders
} from 'lucide-react';

export default function MangaEditor() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addNotification, autosaveStatus, setAutosaveStatus } = useStudioStore();

  const [selectedPanelId, setSelectedPanelId] = useState(null);
  const [currentPageIdx, setCurrentPageIdx] = useState(0);
  const [isBatchGenerating, setIsBatchGenerating] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0, status: '' });

  // Inspector states for selected panel
  const [dialogueText, setDialogueText] = useState('');
  const [speakerName, setSpeakerName] = useState('Ren');
  const [bubbleType, setBubbleType] = useState('speech');
  const [narrationText, setNarrationText] = useState('');
  const [sfxText, setSfxText] = useState('');
  const [imagePrompt, setImagePrompt] = useState('');

  // Fetch project details
  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  });

  // Fetch first chapter for the project (or create if needed)
  const { data: pages = [], isLoading: isPagesLoading } = useQuery({
    queryKey: ['mangaPages', projectId],
    queryFn: () => mangaApi.getProjectPages(projectId),
    enabled: !!projectId,
  });

  const currentPage = pages[currentPageIdx] || null;
  const currentPanels = currentPage?.panels || [];
  const selectedPanel = currentPanels.find((p) => p.id === selectedPanelId) || currentPanels[0] || null;

  useEffect(() => {
    if (selectedPanel) {
      setSelectedPanelId(selectedPanel.id);
      setImagePrompt(selectedPanel.image_prompt || '');
      if (selectedPanel.dialogue && selectedPanel.dialogue.length > 0) {
        setDialogueText(selectedPanel.dialogue[0].text || '');
        setSpeakerName(selectedPanel.dialogue[0].speaker_name || 'Character');
        setBubbleType(selectedPanel.dialogue[0].bubble_type || 'speech');
      } else {
        setDialogueText('');
      }
      if (selectedPanel.narration && selectedPanel.narration.length > 0) {
        setNarrationText(selectedPanel.narration[0].text || '');
      } else {
        setNarrationText('');
      }
      if (selectedPanel.sound_effects && selectedPanel.sound_effects.length > 0) {
        setSfxText(selectedPanel.sound_effects[0].text || '');
      } else {
        setSfxText('');
      }
    }
  }, [selectedPanelId, currentPageIdx, pages]);

  // Update Panel Mutation (dialogue, text, prompts)
  const updatePanelMutation = useMutation({
    mutationFn: ({ panelId, payload }) => mangaApi.updatePanel(panelId, payload),
    onMutate: () => setAutosaveStatus('saving'),
    onSuccess: () => {
      setAutosaveStatus('saved');
      queryClient.invalidateQueries({ queryKey: ['mangaPages', projectId] });
      setTimeout(() => setAutosaveStatus('idle'), 2000);
    },
    onError: (err) => {
      setAutosaveStatus('idle');
      addNotification(`Failed to save panel: ${err.message}`, 'error');
    }
  });

  // Single panel targeted image regeneration
  const regenMutation = useMutation({
    mutationFn: (panelId) => mangaApi.regeneratePanel(panelId, { custom_prompt: imagePrompt }),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ['mangaPages', projectId] });
      addNotification(`Panel ${updated.panel_number} artwork regenerated!`, 'success');
    },
    onError: (err) => {
      addNotification(`Artwork generation error: ${err.message}`, 'error');
    }
  });

  // Batch generate all panels for the current page
  const handleBatchGeneratePage = async () => {
    if (!currentPanels || currentPanels.length === 0) return;
    setIsBatchGenerating(true);
    addNotification('Starting page panel generation (FLUX)...', 'info');

    try {
      for (let i = 0; i < currentPanels.length; i++) {
        const p = currentPanels[i];
        setBatchProgress({
          current: i + 1,
          total: currentPanels.length,
          status: `Generating panel ${p.panel_number}...`
        });

        await mangaApi.regeneratePanel(p.id, {
          custom_prompt: p.image_prompt || p.script || 'Dynamic manga panel'
        });

        queryClient.invalidateQueries({ queryKey: ['mangaPages', projectId] });
        addNotification(`Panel ${p.panel_number} generated!`, 'success');

        if (i < currentPanels.length - 1) {
          for (let sec = 46; sec > 0; sec--) {
            setBatchProgress({
              current: i + 1,
              total: currentPanels.length,
              status: `Free tier cooldown: ready in ${sec}s...`
            });
            await new Promise((res) => setTimeout(res, 1000));
          }
        }
      }
      addNotification('All page panels generated successfully!', 'success');
    } catch (err) {
      addNotification(`Batch generation stopped: ${err.message}`, 'error');
    } finally {
      setIsBatchGenerating(false);
      setBatchProgress({ current: 0, total: 0, status: '' });
      queryClient.invalidateQueries({ queryKey: ['mangaPages', projectId] });
    }
  };

  // Handle panel text save
  const handleSaveTextChanges = () => {
    if (!selectedPanel) return;

    const newDialogue = dialogueText.trim() ? [{
      speaker_name: speakerName.trim() || 'Hero',
      text: dialogueText.trim(),
      bubble_type: bubbleType,
      x: 20.0,
      y: 18.0
    }] : [];

    const newNarration = narrationText.trim() ? [{
      text: narrationText.trim(),
      box_type: 'caption',
      x: 6.0,
      y: 6.0
    }] : [];

    const newSfx = sfxText.trim() ? [{
      text: sfxText.trim(),
      sfx_type: 'dramatic',
      x: 60.0,
      y: 60.0,
      size: 'medium'
    }] : [];

    updatePanelMutation.mutate({
      panelId: selectedPanel.id,
      payload: {
        image_prompt: imagePrompt.trim(),
        dialogue: newDialogue,
        narration: newNarration,
        sound_effects: newSfx
      }
    });
  };

  const isRTL = project?.reading_direction === 'right-to-left';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      {/* Top Editor Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#212638] mb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-950 border border-violet-800/40 flex items-center justify-center text-violet-400">
            <Palette className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white font-['Plus_Jakarta_Sans'] flex items-center gap-2">
              <span>Interactive Manga Canvas</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800/40">
                {isRTL ? "RTL Manga Pacing (<-)" : "LTR Western Pacing (->)"}
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Live panel composition, editable speech bubbles, narration boxes, and targeted panel art regeneration
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Autosave status indicator */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
            {autosaveStatus === 'saving' && (
              <>
                <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                <span className="text-amber-400">Saving...</span>
              </>
            )}
            {autosaveStatus === 'saved' && (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Autosaved</span>
              </>
            )}
            {autosaveStatus === 'idle' && (
              <span>Studio Sync Active</span>
            )}
          </div>

          <button
            disabled={isBatchGenerating || currentPanels.length === 0}
            onClick={handleBatchGeneratePage}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md transition-all disabled:opacity-50"
            title="Generate real FLUX artwork for all panels on this page"
          >
            {isBatchGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>{batchProgress.status || `Generating (${batchProgress.current}/${batchProgress.total})...`}</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Generate All Panels</span>
              </>
            )}
          </button>

          <button
            onClick={() => navigate(`/projects/${projectId}/reader`)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#141824] hover:bg-[#1d2234] border border-[#262c3e] text-slate-200 text-xs font-semibold transition-colors"
          >
            <BookMarked className="w-3.5 h-3.5 text-violet-400" />
            <span>Open Reader</span>
          </button>
        </div>
      </div>

      {isPagesLoading ? (
        <div className="py-24 text-center text-xs text-slate-500">Loading page layout...</div>
      ) : pages.length === 0 ? (
        <div className="py-20 text-center rounded-2xl border border-dashed border-[#242938] max-w-lg mx-auto">
          <Palette className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No Manga Pages Assembled</h3>
          <p className="text-xs text-slate-400 mb-4">
            Generate Chapter 1 from the Story Bible workspace to launch the Manga Director and Art Generation agents.
          </p>
          <button
            onClick={() => navigate(`/projects/${projectId}`)}
            className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs transition-all"
          >
            Go to Story Bible
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Center Column: Large Manga Page Canvas (8 cols) */}
          <div className="lg:col-span-8 flex flex-col items-center">
            {/* Page Navigation Header */}
            <div className="w-full flex items-center justify-between px-2 mb-3 text-xs text-slate-400">
              <span className="font-semibold text-slate-200">
                Page {currentPage?.page_number || 1} of {pages.length}
              </span>

              <div className="flex items-center gap-1">
                <button
                  disabled={currentPageIdx === 0}
                  onClick={() => setCurrentPageIdx((prev) => Math.max(0, prev - 1))}
                  className="p-1.5 rounded bg-[#161a26] text-slate-300 hover:text-white disabled:opacity-30 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={currentPageIdx >= pages.length - 1}
                  onClick={() => setCurrentPageIdx((prev) => Math.min(pages.length - 1, prev + 1))}
                  className="p-1.5 rounded bg-[#161a26] text-slate-300 hover:text-white disabled:opacity-30 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* The Manga Page Frame */}
            <div className="w-full max-w-[640px] aspect-[1/1.414] bg-[#0a0b0e] border-4 border-[#282d3e] rounded-xl p-4 shadow-2xl relative flex flex-col justify-between select-none">
              {/* Header Label */}
              <div className="text-[10px] text-slate-600 font-mono tracking-wider mb-2 flex justify-between">
                <span>{project?.title?.toUpperCase()}</span>
                <span>PAGE {currentPage?.page_number}</span>
              </div>

              {/* 2x2 Panels Grid */}
              <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-3">
                {currentPanels.map((panel) => {
                  const isSelected = selectedPanel?.id === panel.id;
                  return (
                    <div
                      key={panel.id}
                      onClick={() => setSelectedPanelId(panel.id)}
                      className={`relative rounded-lg overflow-hidden border-2 cursor-pointer transition-all flex flex-col justify-between p-3 ${
                        isSelected
                          ? 'border-violet-500 ring-2 ring-violet-500/50 shadow-lg'
                          : 'border-[#2d3345] hover:border-slate-500'
                      } ${panel.image_url ? 'bg-black' : 'bg-[#121520]'}`}
                    >
                      {/* Background Artwork */}
                      {panel.image_url && (
                        <img
                          src={panel.image_url}
                          alt={`Panel ${panel.panel_number}`}
                          className="absolute inset-0 w-full h-full object-cover pointer-events-none"
                        />
                      )}

                      {/* Semi-transparent dark vignette if image exists */}
                      {panel.image_url && (
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20 pointer-events-none" />
                      )}

                      {/* Top: Narration Box */}
                      <div className="relative z-10 self-start">
                        {panel.narration && panel.narration.length > 0 && (
                          <div className="narration-box text-[11px] shadow-md">
                            {panel.narration[0].text}
                          </div>
                        )}
                      </div>

                      {/* Middle: Dialogue Speech Bubble */}
                      <div className="relative z-10 self-center my-auto">
                        {panel.dialogue && panel.dialogue.length > 0 ? (
                          <div className={panel.dialogue[0].bubble_type === 'thought' ? 'thought-bubble' : 'speech-bubble'}>
                            <p className="text-[9px] uppercase tracking-wider text-purple-700 font-bold mb-0.5">
                              {panel.dialogue[0].speaker_name}
                            </p>
                            <p className="text-xs">{panel.dialogue[0].text}</p>
                          </div>
                        ) : !panel.image_url ? (
                          <div className="text-center text-slate-500 text-xs">
                            <span className="font-bold text-violet-400 block mb-1">PANEL {panel.panel_number}</span>
                            <span>{panel.script || 'Director script pending...'}</span>
                          </div>
                        ) : null}
                      </div>

                      {/* Bottom: Sound Effect Tag & Panel Badge */}
                      <div className="relative z-10 flex items-center justify-between w-full">
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-black/70 text-slate-400">
                          #{panel.panel_number}
                        </span>

                        {panel.sound_effects && panel.sound_effects.length > 0 && (
                          <span className="sound-effect-tag text-purple-400 text-sm">
                            {panel.sound_effects[0].text}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Panel Inspector & Targeted Regeneration (4 cols) */}
          <div className="lg:col-span-4 space-y-5">
            {selectedPanel ? (
              <div className="p-5 rounded-2xl bg-[#121520] border border-[#212638] shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-[#212638]">
                  <h3 className="font-bold text-sm text-white flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-violet-400" />
                    <span>Panel {selectedPanel.panel_number} Inspector</span>
                  </h3>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    selectedPanel.status === 'generated' ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {selectedPanel.status}
                  </span>
                </div>

                {/* Speech Bubble / Dialogue Field */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                    <MessageSquare className="w-3.5 h-3.5 text-violet-400" />
                    <span>Character Dialogue</span>
                  </label>
                  <div className="grid grid-cols-2 gap-2 mb-2">
                    <input
                      type="text"
                      value={speakerName}
                      onChange={(e) => setSpeakerName(e.target.value)}
                      placeholder="Speaker"
                      className="px-2.5 py-1.5 rounded-lg bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none"
                    />
                    <select
                      value={bubbleType}
                      onChange={(e) => setBubbleType(e.target.value)}
                      className="px-2.5 py-1.5 rounded-lg bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none"
                    >
                      <option value="speech">Speech Bubble</option>
                      <option value="thought">Thought Bubble</option>
                    </select>
                  </div>
                  <textarea
                    rows={2}
                    value={dialogueText}
                    onChange={(e) => setDialogueText(e.target.value)}
                    placeholder="Enter spoken lines..."
                    className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                  />
                </div>

                {/* Narration Box */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Narration / Caption Box
                  </label>
                  <input
                    type="text"
                    value={narrationText}
                    onChange={(e) => setNarrationText(e.target.value)}
                    placeholder="e.g. Midnight in the outer ruins..."
                    className="w-full px-3 py-1.5 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                  />
                </div>

                {/* Sound Effects */}
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
                    <Volume2 className="w-3.5 h-3.5 text-violet-400" />
                    <span>Sound Effect (SFX)</span>
                  </label>
                  <input
                    type="text"
                    value={sfxText}
                    onChange={(e) => setSfxText(e.target.value)}
                    placeholder="e.g. CLANG!, ROAR!, ZSHHH!"
                    className="w-full px-3 py-1.5 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                  />
                </div>

                {/* Save text button */}
                <button
                  type="button"
                  onClick={handleSaveTextChanges}
                  className="w-full py-2 rounded-xl bg-[#1c2132] hover:bg-[#252b40] text-slate-200 font-semibold text-xs border border-[#2d3448] transition-colors"
                >
                  Apply Text Overlays
                </button>

                {/* Image Prompt & Targeted AI Generation */}
                <div className="pt-3 border-t border-[#212638] space-y-2">
                  <label className="block text-xs font-semibold text-violet-300">
                    Panel Image Prompt (Cloudflare Flux Schnell)
                  </label>
                  <textarea
                    rows={3}
                    value={imagePrompt}
                    onChange={(e) => setImagePrompt(e.target.value)}
                    placeholder="Dramatic high contrast manga panel..."
                    className="w-full p-2.5 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 font-mono focus:outline-none focus:border-violet-500"
                  />
                  <button
                    onClick={() => regenMutation.mutate(selectedPanel.id)}
                    disabled={regenMutation.isPending}
                    className="w-full py-2.5 px-4 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
                  >
                    {regenMutation.isPending ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        <span>Generating Panel Art...</span>
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-3.5 h-3.5" />
                        <span>Regenerate Panel Artwork</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-500 rounded-2xl bg-[#121520] border border-[#212638]">
                Select a panel on the canvas to edit dialogue or regenerate artwork.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

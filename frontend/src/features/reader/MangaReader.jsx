import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '../../api/projects';
import { mangaApi } from '../../api/manga';
import { exportsApi } from '../../api/exports';
import { useStudioStore } from '../../stores/studioStore';
import { 
  ChevronLeft, 
  ChevronRight, 
  Maximize2, 
  Minimize2, 
  Download, 
  BookOpen, 
  ArrowLeft,
  Compass,
  FileDown
} from 'lucide-react';

const formatSpeakerName = (name) => {
  if (!name) return 'Character';
  let clean = String(name).trim();
  if (clean.includes(':')) clean = clean.split(':')[0].trim();
  if (clean.includes('(')) clean = clean.split('(')[0].trim();
  return clean || 'Character';
};

export default function MangaReader() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { addNotification } = useStudioStore();

  const [currentPageIdx, setCurrentPageIdx] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [readingDirection, setReadingDirection] = useState('right-to-left');

  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  });

  const { data: pages = [], isLoading } = useQuery({
    queryKey: ['mangaPages', projectId],
    queryFn: () => mangaApi.getProjectPages(projectId),
    enabled: !!projectId,
  });

  const activePage = pages[currentPageIdx] || null;
  const isRTL = readingDirection === 'right-to-left';

  const handleNextPage = () => {
    if (currentPageIdx < pages.length - 1) {
      setCurrentPageIdx(currentPageIdx + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPageIdx > 0) {
      setCurrentPageIdx(currentPageIdx - 1);
    }
  };

  const handleExportPDF = async () => {
    try {
      const proj = await projectsApi.get(projectId);
      if (!proj.chapters || proj.chapters.length === 0) {
        addNotification('No chapter found to export', 'error');
        return;
      }
      addNotification('Generating print-ready PDF with ReportLab...', 'info');
      const exportRes = await exportsApi.exportChapter(proj.chapters[0].id, {
        format: 'pdf',
        page_size: 'B5',
        reading_direction: readingDirection,
        include_cover: true
      });
      window.open(exportsApi.getDownloadUrl(exportRes.id), '_blank');
      addNotification('Manga PDF download started!', 'success');
    } catch (err) {
      addNotification(`Export failed: ${err.message}`, 'error');
    }
  };

  return (
    <div className={`min-h-[88vh] bg-[#08090d] text-white flex flex-col ${isFullscreen ? 'fixed inset-0 z-50' : 'py-6 px-4'}`}>
      {/* Reader Controls Toolbar */}
      <div className="max-w-5xl mx-auto w-full flex items-center justify-between pb-4 border-b border-[#1f2434] mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(`/projects/${projectId}/editor`)}
            className="p-1.5 rounded-lg bg-[#141724] border border-[#262c3e] text-slate-300 hover:text-white transition-colors"
            title="Back to Editor"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h2 className="text-sm font-bold text-white font-['Plus_Jakarta_Sans'] line-clamp-1">
              {project?.title || "Manga Reader"}
            </h2>
            <p className="text-[10px] text-slate-400">
              Page {pages.length > 0 ? currentPageIdx + 1 : 0} of {pages.length}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Reading Direction Toggle */}
          <button
            onClick={() => setReadingDirection(prev => prev === 'right-to-left' ? 'left-to-right' : 'right-to-left')}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#141724] border border-[#262c3e] text-xs text-slate-300 hover:text-white transition-colors"
          >
            <Compass className="w-3.5 h-3.5 text-violet-400" />
            <span>{isRTL ? "RTL (Manga)" : "LTR (Comic)"}</span>
          </button>

          {/* Download PDF button */}
          <button
            onClick={handleExportPDF}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 transition-all"
          >
            <FileDown className="w-4 h-4" />
            <span>Download PDF</span>
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg bg-[#141724] border border-[#262c3e] text-slate-300 hover:text-white transition-colors"
            title="Toggle Fullscreen"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Reader Page Viewport */}
      {isLoading ? (
        <div className="flex-1 flex items-center justify-center text-xs text-slate-500">Loading reader...</div>
      ) : pages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
          <BookOpen className="w-12 h-12 text-slate-600 mb-3" />
          <h3 className="text-base font-bold text-white mb-1">No Pages to Display</h3>
          <p className="text-xs text-slate-400 mb-4">Generate panels in the editor first before reading.</p>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center relative max-w-4xl mx-auto w-full">
          {/* Navigation Arrows */}
          <button
            onClick={isRTL ? handleNextPage : handlePrevPage}
            disabled={isRTL ? currentPageIdx >= pages.length - 1 : currentPageIdx === 0}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full bg-black/60 hover:bg-black/90 text-white disabled:opacity-20 border border-slate-700 transition-all backdrop-blur-sm"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          <button
            onClick={isRTL ? handlePrevPage : handleNextPage}
            disabled={isRTL ? currentPageIdx === 0 : currentPageIdx >= pages.length - 1}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full bg-black/60 hover:bg-black/90 text-white disabled:opacity-20 border border-slate-700 transition-all backdrop-blur-sm"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* Rendered Manga Page */}
          <div className="w-full max-w-[560px] aspect-[1/1.414] bg-[#0a0b0e] border-2 border-slate-800 rounded-xl p-4 shadow-2xl flex flex-col justify-between select-none relative">
            <div className="text-[10px] text-slate-500 font-mono flex justify-between">
              <span>{project?.title?.toUpperCase()}</span>
              <span>PAGE {activePage?.page_number}</span>
            </div>

            <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-3 my-2">
              {activePage?.panels?.map((panel) => (
                <div
                  key={panel.id}
                  className="relative rounded-lg overflow-hidden border border-slate-700 bg-black flex flex-col justify-between p-3"
                >
                  {panel.image_url && (
                    <img
                      src={panel.image_url}
                      alt={`Panel ${panel.panel_number}`}
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                  )}
                  {panel.image_url && (
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20" />
                  )}

                  <div className="relative z-10 self-start">
                    {panel.narration && panel.narration.length > 0 && (
                      <div className="narration-box text-[10px]">
                        {panel.narration[0].text}
                      </div>
                    )}
                  </div>

                  <div className="relative z-10 self-center my-auto">
                    {panel.dialogue && panel.dialogue.length > 0 && (
                      <div className={panel.dialogue[0].bubble_type === 'thought' ? 'thought-bubble text-[11px]' : 'speech-bubble text-[11px]'}>
                        <p className="text-[9px] uppercase tracking-wider text-purple-700 font-bold mb-0.5">
                          {formatSpeakerName(panel.dialogue[0].speaker_name)}
                        </p>
                        <p>{panel.dialogue[0].text}</p>
                      </div>
                    )}
                  </div>

                  <div className="relative z-10 flex items-center justify-between w-full">
                    <span className="text-[9px] text-slate-400">#{panel.panel_number}</span>
                    {panel.sound_effects && panel.sound_effects.length > 0 && (
                      <span className="sound-effect-tag text-purple-400 text-xs">
                        {panel.sound_effects[0].text}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="text-center text-[10px] text-slate-600">
              {isRTL ? "<- Flip Left to Read Next" : "Flip Right to Read Next ->"}
            </div>
          </div>
        </div>
      )}

      {/* Bottom Thumbnail Ribbon */}
      {pages.length > 0 && (
        <div className="max-w-4xl mx-auto w-full pt-4 border-t border-[#1f2434] mt-4 flex items-center justify-center gap-2 overflow-x-auto pb-2">
          {pages.map((pg, idx) => (
            <button
              key={pg.id}
              onClick={() => setCurrentPageIdx(idx)}
              className={`w-12 h-16 rounded border text-[10px] font-mono flex items-center justify-center transition-all ${
                currentPageIdx === idx
                  ? 'border-violet-500 bg-violet-950/60 text-white font-bold ring-2 ring-violet-500/30'
                  : 'border-slate-800 bg-[#121520] text-slate-400 hover:border-slate-600'
              }`}
            >
              {pg.page_number}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

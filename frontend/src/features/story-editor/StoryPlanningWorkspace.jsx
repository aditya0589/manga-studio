import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../../api/projects';
import { storyApi } from '../../api/story';
import { charactersApi } from '../../api/characters';
import { useStudioStore } from '../../stores/studioStore';
import { useSSE } from '../../hooks/useSSE';
import { 
  Sparkles, 
  BookOpen, 
  Globe, 
  Users, 
  Layers, 
  Clock, 
  CheckCircle2, 
  Loader2, 
  ArrowRight,
  ShieldAlert,
  Play
} from 'lucide-react';

export default function StoryPlanningWorkspace() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addNotification, setActiveProject } = useStudioStore();

  const [activeTab, setActiveTab] = useState('premise');
  const [currentJobId, setCurrentJobId] = useState(null);

  // Stream SSE events when job is running
  useSSE(currentJobId, () => {
    queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    queryClient.invalidateQueries({ queryKey: ['characters', projectId] });
    setCurrentJobId(null);
  });

  const { data: project, isLoading: isProjectLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  });

  React.useEffect(() => {
    if (project) {
      setActiveProject(project);
    }
  }, [project, setActiveProject]);

  const { data: characters = [] } = useQuery({
    queryKey: ['characters', projectId],
    queryFn: () => charactersApi.list(projectId),
    enabled: !!projectId,
  });

  // Story Bible Generation Mutation
  const bibleMutation = useMutation({
    mutationFn: () => storyApi.generateStoryBible(projectId, {}),
    onSuccess: (job) => {
      setCurrentJobId(job.id);
      addNotification('Story Bible Agent started analyzing manuscript...', 'info');
    },
    onError: (err) => {
      addNotification(`Failed to start story bible: ${err.message}`, 'error');
    }
  });

  // Chapter 1 Generation Mutation
  const chapterMutation = useMutation({
    mutationFn: () => storyApi.generateChapter(projectId, {
      title: "Chapter 1: The Midnight Awakening",
      order_index: 1,
      synopsis: project?.synopsis || "Introduction to hero and first trial."
    }),
    onSuccess: (job) => {
      addNotification('Chapter 1 workflow launched with Director and Art agents!', 'success');
      navigate(`/projects/${projectId}/editor`);
    },
    onError: (err) => {
      addNotification(`Failed to launch chapter: ${err.message}`, 'error');
    }
  });

  if (isProjectLoading || !project) {
    return <div className="py-20 text-center text-slate-500 text-sm">Loading project canon...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Top Header with AI Workflow Buttons */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#212638]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-violet-950/70 border border-violet-800/40 text-violet-300">
              {project.genre}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              {project.art_style}
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white font-['Plus_Jakarta_Sans']">
            Story Bible & Planning Workspace
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Maintain canonical facts, character traits, and overarching chapter progressions
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => bibleMutation.mutate()}
            disabled={bibleMutation.isPending || !!currentJobId}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 transition-all disabled:opacity-50"
          >
            {bibleMutation.isPending || currentJobId ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating Bible...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>AI Story Bible Agent</span>
              </>
            )}
          </button>

          <button
            onClick={() => chapterMutation.mutate()}
            disabled={chapterMutation.isPending}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-md shadow-emerald-900/30 transition-all disabled:opacity-50"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Plan & Script Chapter 1</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-[#212638] my-6 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab('premise')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'premise'
              ? 'bg-violet-600/20 text-violet-300 border border-violet-600/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Premise & Synopsis</span>
        </button>

        <button
          onClick={() => setActiveTab('characters')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'characters'
              ? 'bg-violet-600/20 text-violet-300 border border-violet-600/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Canonical Characters ({characters.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('world')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'world'
              ? 'bg-violet-600/20 text-violet-300 border border-violet-600/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
          }`}
        >
          <Globe className="w-4 h-4" />
          <span>World Rules & Locations</span>
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'premise' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] space-y-4 shadow-lg">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-violet-400" />
              Overarching Series Synopsis
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed bg-[#0a0c12] p-4 rounded-xl border border-[#242938]">
              {project.synopsis || "No synopsis generated yet. Click 'AI Story Bible Agent' above to generate one from your documents or genre!"}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] space-y-3">
              <h4 className="text-xs font-bold text-violet-400 uppercase tracking-wider">Target Demographic</h4>
              <p className="text-sm font-semibold text-white">{project.target_audience}</p>
              <p className="text-xs text-slate-400">Pacing, dialogue tone, and emotional stakes are calibrated for this audience.</p>
            </div>

            <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] space-y-3">
              <h4 className="text-xs font-bold text-violet-400 uppercase tracking-wider">Cinematography & Layout</h4>
              <p className="text-sm font-semibold text-white">
                {project.reading_direction === 'right-to-left' ? 'Right-to-Left (Japanese Manga Flow)' : 'Left-to-Right (Western Flow)'}
              </p>
              <p className="text-xs text-slate-400">Panels are arranged from right to left for authentic manga pacing.</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'characters' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">
              Canonical character records are fed to the Art Generation Agent to maintain visual continuity across panels.
            </p>
            <button
              onClick={() => navigate(`/projects/${projectId}/characters`)}
              className="text-xs font-semibold text-violet-400 hover:text-violet-300 flex items-center gap-1"
            >
              <span>Manage in Character Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {characters.length === 0 ? (
            <div className="p-12 text-center rounded-2xl border border-dashed border-[#262c3e]">
              <Users className="w-8 h-8 text-slate-500 mx-auto mb-2" />
              <p className="text-xs text-slate-400">No characters registered yet. Run the AI Story Bible Agent or add characters manually.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {characters.map((char) => (
                <div key={char.id} className="p-5 rounded-2xl bg-[#121520] border border-[#212638] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-violet-950 text-violet-300 border border-violet-800/40 uppercase">
                      {char.role}
                    </span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      char.status === 'approved' ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
                    }`}>
                      {char.status}
                    </span>
                  </div>
                  <h4 className="font-bold text-white text-base">{char.name}</h4>
                  <p className="text-xs text-slate-300 line-clamp-2">{char.appearance || "No appearance described yet."}</p>
                  
                  {char.canon_data?.hair && (
                    <div className="text-[11px] text-slate-400 pt-2 border-t border-[#1d2230]">
                      <span className="text-slate-500 font-medium">Hair:</span> {char.canon_data.hair}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'world' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Globe className="w-4 h-4 text-violet-400" />
              Core Worldbuilding Rules
            </h3>
            <div className="space-y-2 text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-[#0a0c12] border border-[#242938]">
                &bull; Astral techniques deplete stamina when overused, forcing high-contrast monochromatic vision.
              </div>
              <div className="p-3 rounded-xl bg-[#0a0c12] border border-[#242938]">
                &bull; Ancient spirit seals only awaken during midnight forge folding.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

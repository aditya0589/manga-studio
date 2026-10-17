import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../../api/projects';
import { useStudioStore } from '../../stores/studioStore';
import NewProjectWizard from '../projects/NewProjectWizard';
import { 
  FolderPlus, 
  Search, 
  Filter, 
  BookOpen, 
  Calendar, 
  Trash2, 
  Copy, 
  Archive, 
  Sparkles, 
  Layers, 
  Compass,
  ArrowRight,
  Clock
} from 'lucide-react';

export default function ProjectDashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setActiveProject, addNotification } = useStudioStore();

  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects', searchTerm, selectedGenre],
    queryFn: () => projectsApi.list({ search: searchTerm || undefined, genre: selectedGenre || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      addNotification('Project deleted.', 'info');
      setDeleteConfirmId(null);
    },
    onError: (err) => {
      addNotification(`Failed to delete: ${err.message}`, 'error');
    }
  });

  const duplicateMutation = useMutation({
    mutationFn: (project) => projectsApi.create({
      title: `${project.title} (Copy)`,
      synopsis: project.synopsis,
      genre: project.genre,
      art_style: project.art_style,
      reading_direction: project.reading_direction,
      target_audience: project.target_audience
    }),
    onSuccess: (newProj) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      addNotification(`Duplicated project as "${newProj.title}"`, 'success');
    }
  });

  const handleOpenProject = (proj) => {
    setActiveProject(proj);
    navigate(`/projects/${proj.id}`);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-8 border-b border-[#1f2434]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-['Plus_Jakarta_Sans'] tracking-tight">
            Creative Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage your manga projects, character continuity, and publishing pipelines
          </p>
        </div>

        <button
          onClick={() => setIsWizardOpen(true)}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-lg shadow-violet-900/30 transition-all self-start md:self-auto"
        >
          <FolderPlus className="w-4 h-4" />
          <span>New Project</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center gap-3 my-6">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search projects by title..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-[#121520] border border-[#23283a] text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={selectedGenre}
            onChange={(e) => setSelectedGenre(e.target.value)}
            className="w-full sm:w-48 px-3 py-2 rounded-xl bg-[#121520] border border-[#23283a] text-xs text-slate-300 focus:outline-none focus:border-violet-500"
          >
            <option value="">All Genres</option>
            <option value="Action and adventure">Action and adventure</option>
            <option value="Fantasy and dark fantasy">Fantasy & Dark Fantasy</option>
            <option value="Science fiction">Sci-Fi</option>
            <option value="Mystery and thriller">Mystery & Thriller</option>
            <option value="Horror">Horror</option>
            <option value="Romance">Romance</option>
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="py-20 text-center text-slate-500 text-sm">
          Loading projects from studio database...
        </div>
      ) : projects.length === 0 ? (
        <div className="py-16 px-4 rounded-2xl border border-dashed border-[#262c3e] text-center max-w-lg mx-auto my-8">
          <div className="w-12 h-12 rounded-2xl bg-violet-950/50 border border-violet-800/30 flex items-center justify-center text-violet-400 mx-auto mb-4">
            <BookOpen className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-white mb-1">No Projects Found</h3>
          <p className="text-xs text-slate-400 mb-6">
            {searchTerm || selectedGenre 
              ? "No manga titles match your current filters. Try resetting search."
              : "Create your first AI-assisted manga project to get started!"
            }
          </p>
          <button
            onClick={() => setIsWizardOpen(true)}
            className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md transition-all"
          >
            Create New Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((p) => (
            <div
              key={p.id}
              className="group rounded-2xl bg-[#121520] border border-[#212638] hover:border-violet-600/50 transition-all p-5 flex flex-col justify-between shadow-lg hover:shadow-violet-950/20"
            >
              <div>
                {/* Header tags */}
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-violet-950/70 border border-violet-800/40 text-violet-300 uppercase tracking-wider">
                    {p.genre}
                  </span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    p.status === 'published' ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {p.status}
                  </span>
                </div>

                <h3 
                  onClick={() => handleOpenProject(p)}
                  className="font-bold text-white text-base hover:text-violet-400 cursor-pointer transition-colors line-clamp-1"
                >
                  {p.title}
                </h3>

                <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                  {p.synopsis || "No premise supplied yet. Ready for story ingestion and worldbuilding."}
                </p>

                <div className="mt-4 pt-3 border-t border-[#1d2230] flex flex-wrap gap-2 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Palette className="w-3 h-3 text-slate-500" />
                    {p.art_style}
                  </span>
                  <span>&bull;</span>
                  <span className="flex items-center gap-1">
                    <Compass className="w-3 h-3 text-slate-500" />
                    {p.reading_direction === 'right-to-left' ? 'RTL Manga' : 'LTR Comic'}
                  </span>
                </div>
              </div>

              {/* Action buttons footer */}
              <div className="mt-5 pt-3 border-t border-[#1d2230] flex items-center justify-between">
                <button
                  onClick={() => handleOpenProject(p)}
                  className="flex items-center gap-1.5 text-xs font-semibold text-violet-400 hover:text-violet-300 transition-colors"
                >
                  <span>Open Studio</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => duplicateMutation.mutate(p)}
                    className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-white/5 transition-colors"
                    title="Duplicate Project"
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setDeleteConfirmId(p.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded hover:bg-rose-950/20 transition-colors"
                    title="Delete Project"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Delete confirmation modal overlay */}
              {deleteConfirmId === p.id && (
                <div className="mt-3 p-3 rounded-xl bg-rose-950/80 border border-rose-800/80 text-xs text-rose-200">
                  <p className="font-semibold mb-2">Delete this project and all its pages?</p>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => deleteMutation.mutate(p.id)}
                      className="px-3 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-semibold text-[11px]"
                    >
                      Confirm Delete
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(null)}
                      className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px]"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* New Project Modal Wizard */}
      <NewProjectWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
      />
    </div>
  );
}

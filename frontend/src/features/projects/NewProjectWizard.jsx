import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../../api/projects';
import { useStudioStore } from '../../stores/studioStore';
import { Sparkles, X, BookOpen, Palette, Compass, Layers, Loader2 } from 'lucide-react';

const GENRES = [
  "Action and adventure",
  "Fantasy and dark fantasy",
  "Romance",
  "Mystery and thriller",
  "Horror",
  "Science fiction",
  "Supernatural",
  "Drama",
  "Comedy",
  "Custom User Genre"
];

const ART_STYLES = [
  "Traditional Manga B&W",
  "Full-Color Anime Comic",
  "Dark Fantasy Inked Noir",
  "Cyberpunk High-Contrast",
  "Watercolor Manga Shoyo"
];

export default function NewProjectWizard({ isOpen, onClose }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addNotification, setActiveProject } = useStudioStore();

  const [title, setTitle] = useState('');
  const [synopsis, setSynopsis] = useState('');
  const [genre, setGenre] = useState('Action and adventure');
  const [customGenre, setCustomGenre] = useState('');
  const [artStyle, setArtStyle] = useState('Traditional Manga B&W');
  const [readingDirection, setReadingDirection] = useState('right-to-left');
  const [targetAudience, setTargetAudience] = useState('Shonen');

  const createMutation = useMutation({
    mutationFn: (data) => projectsApi.create(data),
    onSuccess: (newProject) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setActiveProject(newProject);
      addNotification(`Project "${newProject.title}" initialized!`, 'success');
      onClose();
      navigate(`/projects/${newProject.id}`);
    },
    onError: (err) => {
      addNotification(`Failed to create project: ${err.message}`, 'error');
    }
  });

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    createMutation.mutate({
      title: title.trim(),
      synopsis: synopsis.trim() || undefined,
      genre: genre === 'Custom User Genre' ? customGenre.trim() || 'Custom' : genre,
      art_style: artStyle,
      reading_direction: readingDirection,
      target_audience: targetAudience
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in">
      <div className="w-full max-w-xl bg-[#12151f] border border-[#272d3e] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#212638] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-violet-950 border border-violet-800/40 flex items-center justify-center text-violet-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Plus_Jakarta_Sans']">Create New Manga Project</h3>
              <p className="text-xs text-slate-400">Define your series premise, genre, and visual direction</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Project Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Spirit Blade: The Shattered Eclipse"
              className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Story Premise / Logline</label>
            <textarea
              rows={3}
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              placeholder="A banished blacksmith discovers an ancient forbidden spirit seal and battles the tyrannical Iron Shogunate..."
              className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Genre</label>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              >
                {GENRES.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Visual Art Style</label>
              <select
                value={artStyle}
                onChange={(e) => setArtStyle(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              >
                {ART_STYLES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          {genre === 'Custom User Genre' && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Specify Custom Genre</label>
              <input
                type="text"
                value={customGenre}
                onChange={(e) => setCustomGenre(e.target.value)}
                placeholder="e.g. Steampunk Noir Mecha"
                className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
              />
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Reading Direction</label>
              <select
                value={readingDirection}
                onChange={(e) => setReadingDirection(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              >
                <option value="right-to-left">Right-to-Left (Traditional Manga)</option>
                <option value="left-to-right">Left-to-Right (Western Comic)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Target Demographics</label>
              <select
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-sm text-slate-200 focus:outline-none focus:border-violet-500"
              >
                <option value="Shonen">Shonen (Teens / Action)</option>
                <option value="Seinen">Seinen (Adult / Dark Themes)</option>
                <option value="Shojo">Shojo (Drama / Romance)</option>
                <option value="General">All Audiences</option>
              </select>
            </div>
          </div>

          <div className="pt-4 flex items-center justify-end gap-3 border-t border-[#212638]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || !title.trim()}
              className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 flex items-center gap-2 disabled:opacity-50"
            >
              {createMutation.isPending ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Initialize Project</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { charactersApi } from '../../api/characters';
import { useStudioStore } from '../../stores/studioStore';
import { 
  Users, 
  UserPlus, 
  CheckCircle2, 
  Upload, 
  ShieldCheck, 
  Sparkles, 
  Image as ImageIcon,
  Loader2,
  Lock
} from 'lucide-react';

export default function CharacterStudio() {
  const { projectId } = useParams();
  const queryClient = useQueryClient();
  const { addNotification } = useStudioStore();

  const [selectedCharId, setSelectedCharId] = useState(null);
  const [isCreating, setIsCreating] = useState(true);
  const [refFile, setRefFile] = useState(null);

  // Form states
  const [name, setName] = useState('');
  const [role, setRole] = useState('Protagonist');
  const [personality, setPersonality] = useState('');
  const [appearance, setAppearance] = useState('');
  const [hair, setHair] = useState('');
  const [eyes, setEyes] = useState('');
  const [clothing, setClothing] = useState('');
  const [consistencyRule, setConsistencyRule] = useState('');

  const { data: characters = [], isLoading } = useQuery({
    queryKey: ['characters', projectId],
    queryFn: () => charactersApi.list(projectId),
    enabled: !!projectId,
  });

  const populateForm = (char) => {
    if (!char) return;
    setName(char.name || '');
    setRole(char.role || 'Protagonist');
    setPersonality(char.personality || '');
    setAppearance(char.appearance || '');
    setHair(char.canon_data?.hair || '');
    setEyes(char.canon_data?.eyes || '');
    setClothing(char.canon_data?.clothing || '');
    const rules = char.canon_data?.visual_consistency_rules || [];
    setConsistencyRule(rules.join('\n'));
  };

  // Sync selected character when characters list loads in TanStack Query v5
  useEffect(() => {
    if (characters && characters.length > 0) {
      if (!selectedCharId && !isCreating) {
        setSelectedCharId(characters[0].id);
        populateForm(characters[0]);
      }
    } else if (!isLoading && characters.length === 0) {
      setIsCreating(true);
    }
  }, [characters, isLoading, selectedCharId, isCreating]);

  const activeChar = characters.find((c) => c.id === selectedCharId);

  const handleSelectChar = (char) => {
    setIsCreating(false);
    setSelectedCharId(char.id);
    populateForm(char);
  };

  const handleStartCreate = () => {
    setIsCreating(true);
    setSelectedCharId(null);
    setName('');
    setRole('Protagonist');
    setPersonality('');
    setAppearance('');
    setHair('');
    setEyes('');
    setClothing('');
    setConsistencyRule('');
  };

  const saveMutation = useMutation({
    mutationFn: (payload) => {
      if (isCreating || !selectedCharId) {
        return charactersApi.create(projectId, payload);
      }
      return charactersApi.update(selectedCharId, payload);
    },
    onSuccess: (savedChar) => {
      queryClient.invalidateQueries({ queryKey: ['characters', projectId] });
      addNotification(`Character "${savedChar.name}" saved successfully!`, 'success');
      setIsCreating(false);
      setSelectedCharId(savedChar.id);
      populateForm(savedChar);
    },
    onError: (err) => {
      addNotification(`Failed to save character: ${err.message}`, 'error');
    }
  });

  const approveMutation = useMutation({
    mutationFn: () => charactersApi.approveDesign(selectedCharId, {
      canonical_appearance: appearance,
      visual_consistency_rules: consistencyRule.split('\n').filter(Boolean)
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['characters', projectId] });
      addNotification('Character design canonically approved!', 'success');
    }
  });

  const uploadRefMutation = useMutation({
    mutationFn: (file) => charactersApi.uploadReference(selectedCharId, file, 'canonical_face'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['characters', projectId] });
      addNotification('Reference image uploaded!', 'success');
      setRefFile(null);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    const payload = {
      name: name.trim(),
      role,
      personality: personality.trim(),
      appearance: appearance.trim(),
      canon_data: {
        hair: hair.trim(),
        eyes: eyes.trim(),
        clothing: clothing.trim(),
        visual_consistency_rules: consistencyRule.split('\n').map((r) => r.trim()).filter(Boolean)
      }
    };
    saveMutation.mutate(payload);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#212638] mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Plus_Jakarta_Sans']">
            Character Continuity Studio
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Build canonical character descriptions, visual consistency rules, and reference image assets
          </p>
        </div>

        <button
          onClick={handleStartCreate}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md transition-all self-start sm:self-auto"
        >
          <UserPlus className="w-4 h-4" />
          <span>Add Character</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Character List */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
            Roster ({characters.length})
          </h3>

          {isLoading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading characters...</div>
          ) : characters.length === 0 ? (
            <div className="p-8 text-center rounded-2xl border border-dashed border-[#242938] text-xs text-slate-500">
              No characters in this project yet. Click "Add Character" to create one.
            </div>
          ) : (
            <div className="space-y-2">
              {characters.map((char) => (
                <div
                  key={char.id}
                  onClick={() => handleSelectChar(char)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${
                    selectedCharId === char.id && !isCreating
                      ? 'bg-violet-950/40 border-violet-600'
                      : 'bg-[#121520] border-[#212638] hover:border-slate-700'
                  }`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-sm text-white">{char.name}</h4>
                      {char.status === 'approved' && (
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" title="Canonically Approved" />
                      )}
                    </div>
                    <span className="text-[11px] text-slate-400">{char.role}</span>
                  </div>

                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                    char.status === 'approved' ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {char.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Character Editor & Reference Uploader */}
        <div className="lg:col-span-8 space-y-6">
          <form onSubmit={handleSubmit} className="p-6 rounded-2xl bg-[#121520] border border-[#212638] space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#212638]">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Users className="w-4 h-4 text-violet-400" />
                <span>{isCreating ? "New Character Profile" : `Editing: ${name || 'Character'}`}</span>
              </h3>

              {!isCreating && activeChar && (
                <button
                  type="button"
                  onClick={() => approveMutation.mutate()}
                  disabled={activeChar.status === 'approved' || approveMutation.isPending}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950 border border-emerald-700/60 text-emerald-400 font-semibold text-xs hover:bg-emerald-900/40 transition-colors disabled:opacity-50"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>{activeChar.status === 'approved' ? 'Canonical Design Approved' : 'Approve Canon Design'}</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Character Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Ren Kurogane"
                  className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Narrative Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-200 focus:outline-none focus:border-violet-500"
                >
                  <option value="Protagonist">Protagonist</option>
                  <option value="Antagonist">Antagonist</option>
                  <option value="Supporting">Supporting Ally</option>
                  <option value="Mentor">Mentor / Elder</option>
                  <option value="Rival">Rival</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Canonical Appearance Description *</label>
              <textarea
                rows={3}
                required
                value={appearance}
                onChange={(e) => setAppearance(e.target.value)}
                placeholder="Jet-black spiky hair with single white streak, piercing silver eyes, tattered indigo blacksmith haori, bandages on arms."
                className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Hair & Color</label>
                <input
                  type="text"
                  value={hair}
                  onChange={(e) => setHair(e.target.value)}
                  placeholder="e.g. Spiky black with white bangs"
                  className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Eye Shape & Color</label>
                <input
                  type="text"
                  value={eyes}
                  onChange={(e) => setEyes(e.target.value)}
                  placeholder="e.g. Sharp mercury silver"
                  className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Clothing / Outfit</label>
                <input
                  type="text"
                  value={clothing}
                  onChange={(e) => setClothing(e.target.value)}
                  placeholder="e.g. Indigo haori, wrapped sash"
                  className="w-full px-3 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Visual Consistency Rules (One per line)
              </label>
              <textarea
                rows={2}
                value={consistencyRule}
                onChange={(e) => setConsistencyRule(e.target.value)}
                placeholder="White streak must always be on the right side. Katana hilt is wrapped in blackened iron."
                className="w-full px-3.5 py-2 rounded-xl bg-[#0a0c12] border border-[#262c3d] text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-violet-500"
              />
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={saveMutation.isPending || !name.trim()}
                className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-semibold text-xs shadow-md shadow-violet-900/30 flex items-center gap-2 disabled:opacity-50"
              >
                {saveMutation.isPending ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>{isCreating ? "Create Character" : "Update Canon Profile"}</span>
                )}
              </button>
            </div>
          </form>

          {/* Reference Images Section */}
          {!isCreating && activeChar && (
            <div className="p-6 rounded-2xl bg-[#121520] border border-[#212638] shadow-lg space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#212638]">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <ImageIcon className="w-4 h-4 text-violet-400" />
                  Reference Images ({activeChar.references?.length || 0})
                </h4>
              </div>

              <div className="flex flex-wrap gap-4 items-center">
                {activeChar.references?.map((ref) => (
                  <div key={ref.id} className="w-28 h-28 rounded-xl border border-slate-700 bg-black overflow-hidden relative group">
                    {ref.image_url ? (
                      <img src={ref.image_url} alt="Ref" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-600 text-xs">Image</div>
                    )}
                    <span className="absolute bottom-1 left-1 right-1 text-[9px] bg-black/80 px-1 py-0.5 rounded text-center text-slate-300 truncate">
                      {ref.reference_type}
                    </span>
                  </div>
                ))}

                {/* Upload reference button */}
                <label className="w-28 h-28 rounded-xl border-2 border-dashed border-[#293042] hover:border-violet-500/50 flex flex-col items-center justify-center cursor-pointer transition-colors text-slate-500 hover:text-slate-300">
                  <Upload className="w-5 h-5 mb-1 text-violet-400" />
                  <span className="text-[10px] font-semibold">Upload Ref</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        uploadRefMutation.mutate(e.target.files[0]);
                      }
                    }}
                    className="hidden"
                  />
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

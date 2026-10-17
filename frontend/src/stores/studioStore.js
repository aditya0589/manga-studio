import { create } from 'zustand';

export const useStudioStore = create((set, get) => ({
  activeProject: null,
  activeChapter: null,
  activePageNumber: 1,
  selectedPanelId: null,
  autosaveStatus: 'idle', // 'idle' | 'saving' | 'saved'
  notifications: [],
  currentJob: null, // { id, progress, stage, status }

  setActiveProject: (project) => set({ activeProject: project }),
  setActiveChapter: (chapter) => set({ activeChapter: chapter }),
  setActivePageNumber: (pageNumber) => set({ activePageNumber: pageNumber }),
  setSelectedPanelId: (panelId) => set({ selectedPanelId: panelId }),
  setAutosaveStatus: (status) => set({ autosaveStatus: status }),

  setCurrentJob: (job) => set({ currentJob: job }),
  updateJobProgress: (progress, stage, extra = {}) => set((state) => ({
    currentJob: state.currentJob 
      ? { ...state.currentJob, progress, stage, ...extra } 
      : { progress, stage, status: 'running', ...extra }
  })),

  addNotification: (message, type = 'info') => {
    const id = Date.now();
    set((state) => ({
      notifications: [...state.notifications, { id, message, type }]
    }));
    setTimeout(() => {
      get().removeNotification(id);
    }, 4500);
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id)
    }));
  },
}));

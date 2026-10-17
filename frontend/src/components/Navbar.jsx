import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useStudioStore } from '../stores/studioStore';
import { 
  Sparkles, 
  FolderKanban, 
  BookOpen, 
  Users, 
  UploadCloud, 
  Palette, 
  BookMarked, 
  Download, 
  Settings as SettingsIcon, 
  LogOut,
  ChevronRight
} from 'lucide-react';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { activeProject, currentJob } = useStudioStore();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isProjectRoute = activeProject && location.pathname.startsWith('/projects/');

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#222736] bg-[#0c0e14]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        
        {/* Left: Brand & Breadcrumb */}
        <div className="flex items-center gap-4">
          <Link to={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-900/30 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5 font-['Plus_Jakarta_Sans']">
                MANGA <span className="text-violet-400">STUDIO</span>
              </span>
              <span className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">Agentic Creative Suite</span>
            </div>
          </Link>

          {isProjectRoute && (
            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-[#222736]">
              <ChevronRight className="w-4 h-4 text-slate-600" />
              <Link 
                to={`/projects/${activeProject.id}`} 
                className="text-xs font-semibold px-2.5 py-1 rounded bg-violet-950/40 text-violet-300 border border-violet-800/40 max-w-[180px] truncate hover:border-violet-600 transition-colors"
              >
                {activeProject.title}
              </Link>
            </div>
          )}
        </div>

        {/* Center: Workspace Navigation Links */}
        {isAuthenticated && activeProject && isProjectRoute && (
          <nav className="hidden lg:flex items-center gap-1">
            <Link
              to={`/projects/${activeProject.id}`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                location.pathname === `/projects/${activeProject.id}` 
                  ? 'bg-violet-600 text-white shadow-sm shadow-purple-900/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#161924]'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              Story Bible
            </Link>

            <Link
              to={`/projects/${activeProject.id}/characters`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                location.pathname.includes('/characters') 
                  ? 'bg-violet-600 text-white shadow-sm shadow-purple-900/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#161924]'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Characters
            </Link>

            <Link
              to={`/projects/${activeProject.id}/uploads`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                location.pathname.includes('/uploads') 
                  ? 'bg-violet-600 text-white shadow-sm shadow-purple-900/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#161924]'
              }`}
            >
              <UploadCloud className="w-3.5 h-3.5" />
              Uploads
            </Link>

            <Link
              to={`/projects/${activeProject.id}/editor`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                location.pathname.includes('/editor') 
                  ? 'bg-violet-600 text-white shadow-sm shadow-purple-900/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#161924]'
              }`}
            >
              <Palette className="w-3.5 h-3.5" />
              Manga Editor
            </Link>

            <Link
              to={`/projects/${activeProject.id}/reader`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                location.pathname.includes('/reader') 
                  ? 'bg-violet-600 text-white shadow-sm shadow-purple-900/50' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#161924]'
              }`}
            >
              <BookMarked className="w-3.5 h-3.5" />
              Reader
            </Link>
          </nav>
        )}

        {/* Right: Actions, Status & User Menu */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-[#161924] transition-colors"
                title="All Projects"
              >
                <FolderKanban className="w-4 h-4 text-violet-400" />
                <span>Projects</span>
              </Link>

              <Link
                to="/settings"
                className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-[#161924] transition-colors"
                title="Studio Settings"
              >
                <SettingsIcon className="w-4 h-4" />
              </Link>

              <div className="hidden sm:flex flex-col text-right pr-1">
                <span className="text-xs font-semibold text-slate-200">{user?.email?.split('@')[0]}</span>
                <span className="text-[10px] text-slate-500 truncate max-w-[120px]">{user?.email}</span>
              </div>

              <button
                onClick={handleLogout}
                className="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-rose-950/20 transition-colors"
                title="Sign Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="text-xs font-semibold px-3.5 py-2 rounded-lg text-slate-300 hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-xs font-semibold px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-900/30 transition-all hover:shadow-violet-900/50"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Real-time generation progress banner */}
      {currentJob && currentJob.status === 'running' && (
        <div className="w-full bg-violet-950/90 border-t border-violet-800/40 px-4 py-1.5 flex items-center justify-between text-xs text-violet-200">
          <div className="flex items-center gap-2 max-w-xl truncate">
            <span className="inline-block w-2 h-2 rounded-full bg-violet-400 animate-ping" />
            <span className="font-semibold text-white">Agentic Workflow:</span>
            <span className="truncate">{currentJob.stage || 'Processing manga assets...'}</span>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <span className="font-mono font-bold text-violet-300">{currentJob.progress || 0}%</span>
            <div className="w-24 h-1.5 bg-violet-900/60 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-violet-500 to-indigo-400 transition-all duration-300"
                style={{ width: `${currentJob.progress || 0}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

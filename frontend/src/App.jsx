import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import Navbar from './components/Navbar';
import NotificationToast from './components/NotificationToast';
import LandingPage from './features/LandingPage';
import AuthPage from './features/auth/AuthPage';
import ProjectDashboard from './features/dashboard/ProjectDashboard';
import StoryPlanningWorkspace from './features/story-editor/StoryPlanningWorkspace';
import CharacterStudio from './features/characters/CharacterStudio';
import UploadWorkspace from './features/uploads/UploadWorkspace';
import MangaEditor from './features/manga-editor/MangaEditor';
import MangaReader from './features/reader/MangaReader';
import SettingsView from './features/settings/SettingsView';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <div className="min-h-screen bg-[#0a0b0e] text-[#f1f3f9] flex flex-col font-sans">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/register" element={<AuthPage mode="register" />} />

          {/* Protected Creative Studio Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <ProjectDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <ProtectedRoute>
                <StoryPlanningWorkspace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/characters"
            element={
              <ProtectedRoute>
                <CharacterStudio />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/uploads"
            element={
              <ProtectedRoute>
                <UploadWorkspace />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/editor"
            element={
              <ProtectedRoute>
                <MangaEditor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/reader"
            element={
              <ProtectedRoute>
                <MangaReader />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsView />
              </ProtectedRoute>
            }
          />

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <NotificationToast />
    </div>
  );
}

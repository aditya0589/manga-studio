import React from 'react';
import { useStudioStore } from '../stores/studioStore';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

export default function NotificationToast() {
  const { notifications, removeNotification } = useStudioStore();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-md w-full pointer-events-none">
      {notifications.map((n) => {
        let Icon = Info;
        let borderClass = 'border-blue-500/30 text-blue-400 bg-blue-950/80';

        if (n.type === 'success') {
          Icon = CheckCircle2;
          borderClass = 'border-emerald-500/30 text-emerald-400 bg-emerald-950/80';
        } else if (n.type === 'error') {
          Icon = AlertCircle;
          borderClass = 'border-rose-500/30 text-rose-400 bg-rose-950/80';
        } else if (n.type === 'warning') {
          Icon = AlertTriangle;
          borderClass = 'border-amber-500/30 text-amber-400 bg-amber-950/80';
        }

        return (
          <div
            key={n.id}
            className={`pointer-events-auto flex items-center justify-between p-3.5 rounded-lg border backdrop-blur-md shadow-xl transition-all duration-200 animate-in slide-in-from-bottom-3 ${borderClass}`}
          >
            <div className="flex items-center gap-3">
              <Icon className="w-5 h-5 shrink-0" />
              <p className="text-sm font-medium text-slate-100">{n.message}</p>
            </div>
            <button
              onClick={() => removeNotification(n.id)}
              className="p-1 hover:bg-white/10 rounded transition-colors text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
}

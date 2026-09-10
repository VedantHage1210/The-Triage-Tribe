import { useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAdminAuth } from "../context/AdminAuthContext";
import AdminSidebar from "./AdminSidebar";

export default function AdminLayout() {
  const { isAuthenticated } = useAdminAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return (
    <div className="min-h-screen flex">
      <AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile-only top bar with hamburger — the sidebar itself is a
            fixed off-canvas drawer below md, so it needs a trigger. */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-slate-200 bg-white">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-slate-500 hover:text-slate-700 p-1"
            aria-label="Open menu"
          >
            <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
              <path d="M2.5 5H17.5M2.5 10H17.5M2.5 15H17.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </button>
          <span className="text-clinical-teal font-semibold text-sm">Triage Admin</span>
        </div>

        <main className="flex-1 p-4 sm:p-8 bg-bg-soft min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

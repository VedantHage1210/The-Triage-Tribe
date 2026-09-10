import { NavLink, useNavigate } from "react-router-dom";
import { useAdminAuth } from "../context/AdminAuthContext";

const LINKS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/symptoms", label: "Symptoms" },
  { to: "/admin/content", label: "UI Content" },
  { to: "/admin/knowledge-base", label: "Knowledge Base" },
  { to: "/admin/sessions", label: "Sessions" },
];

export default function AdminSidebar({ open, onClose }) {
  const { logout } = useAdminAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <>
      {/* Backdrop — mobile only, shown while the drawer is open */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-30 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-56 bg-white border-r border-slate-200
          flex flex-col p-4 transform transition-transform duration-200 ease-out
          ${open ? "translate-x-0" : "-translate-x-full"} md:translate-x-0`}
      >
        <div className="flex items-center justify-between mb-6">
          <span className="text-clinical-teal font-semibold">Triage Admin</span>
          <button
            onClick={onClose}
            className="md:hidden text-slate-400 hover:text-slate-600 p-1"
            aria-label="Close menu"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <nav className="flex flex-col gap-1 flex-1">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              onClick={onClose}
              className={({ isActive }) =>
                `px-3 py-2 rounded-lg text-sm ${
                  isActive ? "bg-clinical-teal/10 text-clinical-teal font-medium" : "text-slate-600 hover:bg-slate-50"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <button onClick={handleLogout} className="text-sm text-slate-500 hover:text-severity-emergency text-left">
          Log out
        </button>
      </aside>
    </>
  );
}

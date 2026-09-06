import { NavLink, useNavigate } from "react-router-dom";
import { useAdminAuth } from "../context/AdminAuthContext";

const LINKS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/symptoms", label: "Symptoms" },
  { to: "/admin/content", label: "UI Content" },
  { to: "/admin/knowledge-base", label: "Knowledge Base" },
  { to: "/admin/sessions", label: "Sessions" },
];

export default function AdminSidebar() {
  const { logout } = useAdminAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/admin/login");
  };

  return (
    <aside className="w-56 bg-white border-r border-slate-200 flex flex-col p-4">
      <div className="text-clinical-teal font-semibold mb-6">Triage Admin</div>
      <nav className="flex flex-col gap-1 flex-1">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
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
  );
}

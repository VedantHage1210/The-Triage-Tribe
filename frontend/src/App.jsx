import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "./context/LanguageContext";
import { AdminAuthProvider } from "./context/AdminAuthContext";
import CategoryGridPage from "./pages/CategoryGridPage";
import TriagePage from "./pages/TriagePage";
import HowItWorksPage from "./pages/HowItWorksPage";
import AdminLoginPage from "./pages/admin/AdminLoginPage";
import AdminLayout from "./components/AdminLayout";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import AdminSymptomsPage from "./pages/admin/AdminSymptomsPage";
import AdminContentPage from "./pages/admin/AdminContentPage";
import AdminKnowledgeBasePage from "./pages/admin/AdminKnowledgeBasePage";
import AdminSessionsPage from "./pages/admin/AdminSessionsPage";

export default function App() {
  return (
    <LanguageProvider>
      <AdminAuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Patient-facing app */}
            <Route path="/" element={<CategoryGridPage />} />
            <Route path="/triage/:category" element={<TriagePage />} />
            <Route path="/how-it-works" element={<HowItWorksPage />} />

            {/* Admin panel */}
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<AdminDashboardPage />} />
              <Route path="symptoms" element={<AdminSymptomsPage />} />
              <Route path="content" element={<AdminContentPage />} />
              <Route path="knowledge-base" element={<AdminKnowledgeBasePage />} />
              <Route path="sessions" element={<AdminSessionsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AdminAuthProvider>
    </LanguageProvider>
  );
}

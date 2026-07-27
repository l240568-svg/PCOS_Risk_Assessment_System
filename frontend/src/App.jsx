import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import { useAuth } from "./auth/auth-context";
import AppShell from "./components/AppShell";
import LoadingScreen from "./components/LoadingScreen";
import DashboardPage from "./pages/DashboardPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DoctorProfilePage from "./pages/DoctorProfilePage";
import PatientsPage from "./pages/PatientsPage";
import PatientProfilePage from "./pages/PatientProfilePage";

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingScreen />;
  }

  return isAuthenticated ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace state={{ from: location }} />
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<DoctorProfilePage />} />
          <Route path="/patients" element={<PatientsPage />} />
          <Route path="/patients/:patientId" element={<PatientProfilePage />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;

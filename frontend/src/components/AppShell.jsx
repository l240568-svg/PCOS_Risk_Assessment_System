import {
  ChevronDown,
  LayoutDashboard,
  LogOut,
  Menu,
  Plus,
  UserRound,
  UsersRound,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { initials } from "../utils/formatters";
import Logo from "./Logo";

const navigation = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/patients", label: "Patients", icon: UsersRound },
  { to: "/profile", label: "Doctor profile", icon: UserRound },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    setMobileOpen(false);
    setProfileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const close = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) setProfileOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  const displayName = user ? `Dr. ${user.first_name} ${user.last_name}` : "Doctor";

  return (
    <div className="app-shell">
      <button
        className={`mobile-backdrop ${mobileOpen ? "is-visible" : ""}`}
        type="button"
        onClick={() => setMobileOpen(false)}
        aria-label="Close navigation"
      />

      <aside className={`sidebar ${mobileOpen ? "is-open" : ""}`}>
        <div className="sidebar-brand-row">
          <Logo to="/dashboard" />
          <button className="icon-button sidebar-close" type="button" onClick={() => setMobileOpen(false)} aria-label="Close navigation">
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav" aria-label="Clinical workspace">
          <p className="nav-label">Workspace</p>
          {navigation.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-support">
          <span>Clinical support</span>
          <strong>PCOS risk assessment</strong>
          <p>Use results alongside your clinical judgment.</p>
        </div>

        <button className="sidebar-user" type="button" onClick={() => navigate("/profile")}>
          <span className="avatar">{initials(user?.first_name, user?.last_name)}</span>
          <span>
            <strong>{displayName}</strong>
            <small>{user?.specialization}</small>
          </span>
        </button>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <button className="icon-button mobile-menu" type="button" onClick={() => setMobileOpen(true)} aria-label="Open navigation">
            <Menu size={21} />
          </button>

          <div className="topbar-context">
            <span>Clinical workspace</span>
            <strong>{displayName}</strong>
          </div>

          <div className="topbar-actions">
            <button className="button button-primary topbar-add" type="button" onClick={() => navigate("/patients?add=1")}>
              <Plus size={17} />
              <span>Add patient</span>
            </button>

            <div className="profile-menu" ref={profileRef}>
              <button className="profile-trigger" type="button" onClick={() => setProfileOpen((open) => !open)} aria-expanded={profileOpen}>
                <span className="avatar avatar-small">{initials(user?.first_name, user?.last_name)}</span>
                <ChevronDown size={16} />
              </button>
              {profileOpen && (
                <div className="profile-popover">
                  <div>
                    <strong>{displayName}</strong>
                    <small>{user?.email}</small>
                  </div>
                  <button type="button" onClick={() => navigate("/profile")}>
                    <UserRound size={17} /> Profile settings
                  </button>
                  <button type="button" onClick={handleLogout}>
                    <LogOut size={17} /> Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

import { Building2, CalendarDays, KeyRound, Mail, MapPin, Save, ShieldCheck, Stethoscope, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiRequest } from "../services/api";
import { useAuth } from "../auth/auth-context";
import { useToast } from "../components/ToastProvider";
import { Field, Spinner } from "../components/ui";
import { formatDate, initials } from "../utils/formatters";

export default function DoctorProfilePage() {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [tab, setTab] = useState("profile");
  const [profile, setProfile] = useState({});
  const [passwords, setPasswords] = useState({ old_password: "", new_password: "", confirm_new_password: "" });
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) setProfile({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      specialization: user.specialization,
      hospital: user.hospital || "",
      clinic_address: user.clinic_address || "",
      license_number: user.license_number,
    });
  }, [user]);

  const updateProfile = (field, value) => setProfile((current) => ({ ...current, [field]: value }));
  const updatePassword = (field, value) => setPasswords((current) => ({ ...current, [field]: value }));

  async function saveProfile(event) {
    event.preventDefault();
    setSaving(true); setProfileError("");
    try {
      await apiRequest("/users/me",{"method":"PATCH","body":JSON.stringify({ ...profile, hospital: profile.hospital.trim() || null, clinic_address: profile.clinic_address.trim() || null })});
      await refreshUser();
      showToast("Professional profile updated.");
    } catch (requestError) { setProfileError(requestError.message); }
    finally { setSaving(false); }
  }

  async function changePassword(event) {
    event.preventDefault();
    setSaving(true); setPasswordError("");
    if (passwords.new_password !== passwords.confirm_new_password) {
      setPasswordError("New password and confirmation do not match.");
      setSaving(false);
      return;
    }
    try {
    await apiRequest("/users/me/password", {
    method: "PATCH",
    body: JSON.stringify(passwords),
  });

  setPasswords({
    old_password: "",
    new_password: "",
    confirm_new_password: "",
  });

  // Revoke tokens and clear the frontend session.
  try {
    await logout();
  } catch {
    // logout() clears local tokens in its finally block.
  }

  navigate("/login", {
    replace: true,
    state: { passwordReset: true },
  });
} catch (requestError) {
  setPasswordError(requestError.message);
} finally {
  setSaving(false);
}
  }

  return (
    <div className="page-stack">
      <header className="page-header"><div><span className="eyebrow">Account settings</span><h1>Doctor profile</h1><p>Manage the professional information shown in your clinical workspace.</p></div></header>

      <section className="doctor-profile-banner">
        <span className="avatar avatar-profile">{initials(user?.first_name, user?.last_name)}</span>
        <div><h2>Dr. {user?.first_name} {user?.last_name}</h2><p>{user?.specialization} {user?.hospital ? `· ${user.hospital}` : ""}</p><span><ShieldCheck size={15} /> Licensed doctor account</span></div>
        <dl><div><dt>Member since</dt><dd>{formatDate(user?.created_at)}</dd></div><div><dt>License</dt><dd>{user?.license_number}</dd></div></dl>
      </section>

      <nav className="tab-bar profile-tabs" aria-label="Profile settings"><button type="button" className={tab === "profile" ? "active" : ""} onClick={() => setTab("profile")}>Professional details</button><button type="button" className={tab === "security" ? "active" : ""} onClick={() => setTab("security")}>Password & security</button></nav>

      {tab === "profile" && <section className="content-panel settings-panel"><div className="panel-header"><div><span className="panel-kicker"><UserRound size={15} /> Profile information</span><h2>Professional details</h2></div></div>{profileError && <div className="form-notice error-notice" role="alert">{profileError}</div>}<form className="settings-form" onSubmit={saveProfile}>
        <div className="form-grid form-grid-two"><Field label="First name" required>{(props) => <input {...props} value={profile.first_name || ""} onChange={(e) => updateProfile("first_name", e.target.value)} required />}</Field><Field label="Last name" required>{(props) => <input {...props} value={profile.last_name || ""} onChange={(e) => updateProfile("last_name", e.target.value)} required />}</Field></div>
        <Field label="Professional email" required>{(props) => <div className="input-with-icon"><Mail size={18} /><input {...props} type="email" aria-readonly="true" className="input-readonly" value={profile.email || ""} readOnly required /></div>}</Field>
        <div className="form-grid form-grid-two"><Field label="Specialization" required>{(props) => <div className="input-with-icon"><Stethoscope size={18} /><select {...props} value={profile.specialization || "Gynecologist"} onChange={(e) => updateProfile("specialization", e.target.value)}><option>Gynecologist</option><option>Endocrinologist</option></select></div>}</Field><Field label="License number" required>{(props) => <input {...props} value={profile.license_number || ""} onChange={(e) => updateProfile("license_number", e.target.value)} required />}</Field></div>
        <Field label="Hospital or clinic">{(props) => <div className="input-with-icon"><Building2 size={18} /><input {...props} value={profile.hospital || ""} onChange={(e) => updateProfile("hospital", e.target.value)} /></div>}</Field>
        <Field label="Clinic address">{(props) => <div className="input-with-icon"><MapPin size={18} /><input {...props} value={profile.clinic_address || ""} onChange={(e) => updateProfile("clinic_address", e.target.value)} /></div>}</Field>
        <div className="settings-actions"><button className="button button-primary" disabled={saving}>{saving ? <Spinner label="Saving changes" /> : <><Save size={17} /> Save changes</>}</button></div>
      </form></section>}

      {tab === "security" && <section className="content-panel settings-panel"><div className="panel-header"><div><span className="panel-kicker"><KeyRound size={15} /> Account security</span><h2>Change password</h2></div></div><div className="security-intro"><span><ShieldCheck size={20} /></span><p>Use at least 8 characters including uppercase, lowercase, and a special character.</p></div>{passwordError && <div className="form-notice error-notice" role="alert">{passwordError}</div>}<form className="settings-form" onSubmit={changePassword}>
        <Field label="Current password" required>{(props) => <input {...props} type="password" value={passwords.old_password} onChange={(e) => updatePassword("old_password", e.target.value)} autoComplete="current-password" required />}</Field>
        <Field label="New password" required>{(props) => <input {...props} type="password" minLength="8" value={passwords.new_password} onChange={(e) => updatePassword("new_password", e.target.value)} autoComplete="new-password" required />}</Field>
        <Field label="Confirm new password" required>{(props) => <input {...props} type="password" minLength="8" value={passwords.confirm_new_password} onChange={(e) => updatePassword("confirm_new_password", e.target.value)} autoComplete="new-password" required />}</Field>
        <div className="settings-actions"><button className="button button-primary" disabled={saving}>{saving ? <Spinner label="Updating password" /> : "Update password"}</button></div>
      </form></section>}
    </div>
  );
}

import {
  Activity,
  ArrowRight,
  ChartNoAxesCombined,
  CheckCircle2,
  ClipboardPlus,
  Menu,
  Search,
  ShieldCheck,
  Sparkles,
  Stethoscope,
  UserRoundPlus,
  X,
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import Logo from "../components/Logo";

const features = [
  {
    icon: UserRoundPlus,
    title: "Patient records",
    text: "Create and organize essential patient information in a focused clinical workspace.",
  },
  {
    icon: ClipboardPlus,
    title: "Guided assessments",
    text: "Capture symptoms, laboratory values, lifestyle factors, and ultrasound findings with clarity.",
  },
  {
    icon: ChartNoAxesCombined,
    title: "Risk overview",
    text: "Review assessment history and quickly identify patients who may need closer attention.",
  },
];

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="landing-nav container">
          <Logo />
          <nav className={`landing-links ${menuOpen ? "is-open" : ""}`} aria-label="Main navigation">
            <a href="#capabilities" onClick={() => setMenuOpen(false)}>Capabilities</a>
            <a href="#workflow" onClick={() => setMenuOpen(false)}>Workflow</a>
            <a href="#clinical-use" onClick={() => setMenuOpen(false)}>Clinical use</a>
            <div className="landing-mobile-actions">
              <Link className="button button-secondary" to="/login">Log in</Link>
              <Link className="button button-primary" to="/register">Create account</Link>
            </div>
          </nav>
          <div className="landing-actions">
            <Link className="button button-ghost" to="/login">Log in</Link>
            <Link className="button button-primary" to="/register">Create account</Link>
          </div>
          <button className="icon-button landing-menu-button" type="button" onClick={() => setMenuOpen((open) => !open)} aria-label="Toggle navigation" aria-expanded={menuOpen}>
            {menuOpen ? <X size={21} /> : <Menu size={21} />}
          </button>
        </div>
      </header>

      <main>
        <section className="hero-section container">
          <div className="hero-copy">
            <span className="eyebrow eyebrow-light"><Sparkles size={15} /> PCOS clinical decision support</span>
            <h1>Focused care starts with a clearer patient picture.</h1>
            <p>
              A modern clinical workspace that helps gynecologists and endocrinologists organize patient data, assess PCOS risk, and review follow-up history.
            </p>
            <div className="hero-actions">
              <Link className="button button-light button-large" to="/register">
                Create doctor account <ArrowRight size={18} />
              </Link>
              <Link className="button button-outline-light button-large" to="/login">Open workspace</Link>
            </div>
            <div className="hero-trust">
              <span><ShieldCheck size={18} /> Doctor-owned records</span>
              <span><CheckCircle2 size={18} /> Guided data entry</span>
            </div>
          </div>

          <div className="hero-image-wrap" aria-label="Doctor reviewing patient care">
            <img
              src="/images/doc.jpg"
              alt="Doctor standing in a bright clinical setting"
            />
            <div className="hero-floating hero-floating-top">
              <span className="mini-icon"><Activity size={17} /></span>
              <span><small>Clinical focus</small><strong>PCOS risk review</strong></span>
            </div>
            <div className="hero-floating hero-floating-bottom">
              <span className="status-dot" />
              <span><small>Workspace</small><strong>Ready for care</strong></span>
            </div>
          </div>

          <div className="hero-stats" aria-label="Platform highlights">
            <div><strong>One</strong><span>organized patient record</span></div>
            <div><strong>3-step</strong><span>guided assessment flow</span></div>
            <div><strong>Live</strong><span>risk overview and history</span></div>
          </div>
        </section>

        <section className="capabilities-section" id="capabilities">
          <div className="container">
            <div className="section-heading">
              <span className="eyebrow">Built around the consultation</span>
              <h2>Everything needed for a smoother assessment workflow</h2>
              <p>Essential tools stay visible and predictable, so attention remains on the patient.</p>
            </div>
            <div className="feature-grid">
              {features.map(({ icon: Icon, title, text }, index) => (
                <article className="feature-card" key={title}>
                  <span className={`feature-icon feature-icon-${index + 1}`}><Icon size={22} /></span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="workflow-section container" id="workflow">
          <div className="workflow-copy">
            <span className="eyebrow">A simple clinical rhythm</span>
            <h2>From patient search to risk review without losing context</h2>
            <p>Each step leads naturally to the next, with responsive layouts for clinic desktops, tablets, and phones.</p>
            <Link to="/register" className="text-link">Set up your workspace <ArrowRight size={17} /></Link>
          </div>
          <ol className="workflow-list">
            <li><span>01</span><div><strong>Find or add a patient</strong><p>Search by name or risk class, or open a guided patient drawer.</p></div><Search size={21} /></li>
            <li><span>02</span><div><strong>Complete the assessment</strong><p>Move through measurements, symptoms, and ultrasound findings.</p></div><Stethoscope size={21} /></li>
            <li><span>03</span><div><strong>Review and follow up</strong><p>See the risk result beside prior assessments and clinical notes.</p></div><ChartNoAxesCombined size={21} /></li>
          </ol>
        </section>

        <section className="clinical-band" id="clinical-use">
          <div className="container clinical-band-inner">
            <div>
              <span className="eyebrow eyebrow-light">Made for responsible clinical use</span>
              <h2>Useful insight, with the doctor still at the center.</h2>
            </div>
            <p>
              PCOS Care presents model output as decision support. It keeps patient context and assessment history visible while leaving diagnosis and treatment decisions with the clinician.
            </p>
          </div>
        </section>

        <section className="landing-cta container">
          <div>
            <span className="eyebrow">Your clinical workspace</span>
            <h2>Bring clarity to every PCOS risk assessment.</h2>
          </div>
          <Link className="button button-primary button-large" to="/register">Create doctor account <ArrowRight size={18} /></Link>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="container footer-inner">
          <Logo />
          <p>Clinical decision support for PCOS risk assessment. Not a substitute for diagnosis.</p>
          <span>© {new Date().getFullYear()} PCOS Care</span>
        </div>
      </footer>
    </div>
  );
}

import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

import Logo from "../components/Logo";

export default function NotFoundPage() {
  return (
    <main className="not-found">
      <Logo />
      <span>404</span>
      <h1>This page is not part of the workspace.</h1>
      <p>The link may be outdated, or the page may have moved.</p>
      <Link className="button button-primary" to="/"><ArrowLeft size={17} /> Return home</Link>
    </main>
  );
}

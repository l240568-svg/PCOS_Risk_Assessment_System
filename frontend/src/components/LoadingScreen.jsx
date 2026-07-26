import Logo from "./Logo";

export default function LoadingScreen() {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <Logo />
      <span className="spinner spinner-large" aria-hidden="true" />
      <span className="sr-only">Loading clinical workspace</span>
    </div>
  );
}

export function Header({ onLogout }: { onLogout: () => void }) {
  return (
    <header className="mb-6 flex items-center justify-between">
      <span className="text-xl font-semibold">Rigi</span>
      <button
        className="text-sm text-slate-600 hover:underline"
        onClick={onLogout}
      >
        Log out
      </button>
    </header>
  );
}

import { NavLink } from "react-router";

function tabClassName({ isActive }: { isActive: boolean }) {
  return isActive
    ? "flex items-center justify-center py-4 text-sm font-medium text-blue-600"
    : "flex items-center justify-center py-4 text-sm font-medium text-slate-500 hover:text-slate-700";
}

export function TabBar() {
  return (
    <nav
      aria-label="Main navigation"
      className="fixed inset-x-0 bottom-0 border-t border-slate-200 bg-white"
    >
      <div className="mx-auto max-w-md grid grid-cols-3">
        <NavLink to="/" end className={tabClassName}>
          Scan
        </NavLink>
        <NavLink to="/tickets" className={tabClassName}>
          Tickets
        </NavLink>
        <NavLink to="/profile" className={tabClassName}>
          Profile
        </NavLink>
      </div>
    </nav>
  );
}

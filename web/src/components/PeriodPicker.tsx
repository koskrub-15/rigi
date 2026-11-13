import type { Period } from "../types";

const OPTIONS: ReadonlyArray<{ value: Period; label: string }> = [
  { value: 1, label: "This month" },
  { value: 3, label: "Last 3 months" },
  { value: 12, label: "This year" },
];

const BASE = "rounded-md py-1.5 text-sm";
const ACTIVE = "bg-white font-medium shadow-sm";
const INACTIVE = "text-slate-600";

export function PeriodPicker({
  value,
  onChange,
}: {
  value: Period;
  onChange: (period: Period) => void;
}) {
  return (
    <div className="grid grid-cols-3 gap-1 rounded-lg bg-slate-200 p-1">
      {OPTIONS.map((option) => {
        const isActive = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={isActive}
            onClick={() => onChange(option.value)}
            className={`${BASE} ${isActive ? ACTIVE : INACTIVE}`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

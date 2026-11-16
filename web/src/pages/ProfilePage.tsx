import { useState } from "react";
import { periodBounds } from "../month";
import type { Period, Stats, Trip } from "../types";
import { StatsView } from "../components/StatsView";
import { TripsList } from "../components/TripsList";
import { cardClass, secondaryButtonClass } from "../styles";
import { PeriodPicker } from "../components/PeriodPicker";
import { useApi } from "../useApi";

export function ProfilePage({ onLogout }: { onLogout: () => void }) {
  const [period, setPeriod] = useState<Period>(1);
  const [dateFrom, dateTo] = periodBounds(period, new Date());
  const params = new URLSearchParams({
    date_from: dateFrom.toISOString(),
    date_to: dateTo.toISOString(),
  });
  const { data: trips, error: tripsError } = useApi<Trip[]>(
    `/trips?${params}`,
    onLogout,
  );

  const { data: stats, error: statsError } = useApi<Stats>(
    `/stats?${params}`,
    onLogout,
  );

  return (
    <div className="flex flex-col gap-4">
      <PeriodPicker value={period} onChange={setPeriod} />
      {stats ? (
        <StatsView stats={stats} />
      ) : statsError ? (
        <section className={cardClass}>
          <p className="text-red-600 text-sm">{statsError}</p>
        </section>
      ) : (
        <section className={cardClass}>Loading…</section>
      )}
      {trips ? (
        <TripsList trips={trips.toReversed()} />
      ) : tripsError ? (
        <section className={cardClass}>
          <p className="text-red-600 text-sm">{tripsError}</p>
        </section>
      ) : (
        <section className={cardClass}>Loading…</section>
      )}
      <button className={`${secondaryButtonClass} w-full`} onClick={onLogout}>
        Log out
      </button>
    </div>
  );
}

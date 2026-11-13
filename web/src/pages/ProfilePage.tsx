import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { periodBounds } from "../month";
import type { Period, Stats, Trip } from "../types";
import { StatsView } from "../components/StatsView";
import { TripsList } from "../components/TripsList";
import { cardClass, secondaryButtonClass } from "../styles";
import { PeriodPicker } from "../components/PeriodPicker";

export function ProfilePage({ onLogout }: { onLogout: () => void }) {
  const [trips, setTrips] = useState<Trip[] | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [period, setPeriod] = useState<Period>(1);
  async function load() {
    const [dateFrom, dateTo] = periodBounds(period, new Date());
    const params = new URLSearchParams({
      date_from: dateFrom.toISOString(),
      date_to: dateTo.toISOString(),
    });

    const tripsResponse = await apiFetch(`/trips?${params}`);
    const statsResponse = await apiFetch(`/stats?${params}`);
    if (!tripsResponse.ok) {
      if (tripsResponse.status === 401) {
        onLogout();
      }
      return;
    }
    if (!statsResponse.ok) {
      if (statsResponse.status === 401) {
        onLogout();
      }
      return;
    }
    const tripsData = await tripsResponse.json();
    const statsData = await statsResponse.json();
    setTrips(tripsData);
    setStats(statsData);
  }

  useEffect(() => {
    setTrips(null);
    setStats(null);
    load();
  }, [period]);

  return (
    <div className="flex flex-col gap-4">
      <PeriodPicker value={period} onChange={setPeriod} />
      {stats ? (
        <StatsView stats={stats} />
      ) : (
        <section className={cardClass}>Loading…</section>
      )}
      {trips ? (
        <TripsList trips={trips.toReversed()} />
      ) : (
        <section className={cardClass}>Loading…</section>
      )}
      <button className={`${secondaryButtonClass} w-full`} onClick={onLogout}>
        Log out
      </button>
    </div>
  );
}

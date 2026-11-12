import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { monthBounds } from "../month";
import type { Bill, Stats, Trip } from "../types";
import { BillView } from "./BillView";
import { ClosedBills } from "./ClosedBills";
import { ScanPanel } from "./ScanPanel";
import { StatsView } from "./StatsView";
import { TripsList } from "./TripList";

export function Home({ onLogout }: { onLogout: () => void }) {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [bill, setBill] = useState<Bill | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  async function load() {
    const [dateFrom, dateTo] = monthBounds(new Date());
    const params = new URLSearchParams({
      date_from: dateFrom.toISOString(),
      date_to: dateTo.toISOString(),
    });

    const tripsResponse = await apiFetch(`/trips`);
    const billResponse = await apiFetch(`/bills/preview?${params}`);
    const statsResponse = await apiFetch(`/stats?${params}`);
    if (!tripsResponse.ok) {
      if (tripsResponse.status === 401) {
        onLogout();
      }
      return;
    }
    if (!billResponse.ok) {
      if (billResponse.status === 401) {
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
    const billData = await billResponse.json();
    const statsData = await statsResponse.json();
    setTrips(tripsData);
    setBill(billData);
    setStats(statsData);
  }

  useEffect(() => {
    load();
  }, []);

  async function scan(scanType: string, code: string) {
    setError("");
    const response = await apiFetch(`/scans`, {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({
        scan_type: scanType,
        timestamp: new Date().toISOString(),
        code: code,
      }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        onLogout();
        return;
      }
      const data = await response.json();
      setError(
        typeof data.detail === "string" ? data.detail : "Invalid QR code",
      );
      return;
    }
    await load();
  }

  return (
    <div className="flex flex-col gap-4">
      <ScanPanel onScan={scan} sendError={error} />
      <TripsList trips={trips} />
      {bill && <BillView bill={bill} />}
      <ClosedBills onLogout={onLogout} />
      {stats && <StatsView stats={stats} />}
    </div>
  );
}

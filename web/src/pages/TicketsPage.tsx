import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { monthBounds } from "../month";
import type { Bill } from "../types";
import { BillView } from "../components/BillView";
import { ClosedBills } from "../components/ClosedBills";

export function TicketsPage({ onLogout }: { onLogout: () => void }) {
  const [bill, setBill] = useState<Bill | null>(null);

  async function load() {
    const [dateFrom, dateTo] = monthBounds(new Date());
    const params = new URLSearchParams({
      date_from: dateFrom.toISOString(),
      date_to: dateTo.toISOString(),
    });

    const billResponse = await apiFetch(`/bills/preview?${params}`);
    if (!billResponse.ok) {
      if (billResponse.status === 401) {
        onLogout();
      }
      return;
    }
    const billData = await billResponse.json();
    setBill(billData);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="flex flex-col gap-4">
      {bill && <BillView bill={bill} />}
      <ClosedBills onLogout={onLogout} />
    </div>
  );
}

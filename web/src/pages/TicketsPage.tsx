import { monthBounds } from "../month";
import type { Bill } from "../types";
import { BillView } from "../components/BillView";
import { ClosedBills } from "../components/ClosedBills";
import { cardClass } from "../styles";
import { useApi } from "../useApi";

export function TicketsPage({ onLogout }: { onLogout: () => void }) {
  const [dateFrom, dateTo] = monthBounds(new Date());
  const params = new URLSearchParams({
    date_from: dateFrom.toISOString(),
    date_to: dateTo.toISOString(),
  });

  const { data: bill, error } = useApi<Bill>(
    `/bills/preview?${params}`,
    onLogout,
  );

  return (
    <div className="flex flex-col gap-4">
      {bill ? (
        <BillView bill={bill} />
      ) : error ? (
        <section className={cardClass}>
          <p className="text-red-600 text-sm">{error}</p>
        </section>
      ) : (
        <section className={cardClass}>Loading…</section>
      )}
      <ClosedBills onLogout={onLogout} />
    </div>
  );
}

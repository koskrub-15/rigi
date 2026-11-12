import { useState, useEffect } from "react";
import "chart.js/auto";

import { buttonClass, cardClass, secondaryButtonClass } from "../styles";

import { previousMonth } from "../month";
import { apiFetch } from "../api";
import type { ClosedBill } from "../types";
import { formatMoney } from "../format";

export function ClosedBills({ onLogout }: { onLogout: () => void }) {
  const [bills, setBills] = useState<ClosedBill[]>([]);
  const [error, setError] = useState("");
  const [[year, month]] = useState(() => previousMonth(new Date()));
  const label = `${year}-${String(month).padStart(2, "0")}`;
  const payment = new URLSearchParams(window.location.search).get("payment");

  async function load() {
    setError("");
    const billResponse = await apiFetch(`/bills`);
    if (!billResponse.ok) {
      if (billResponse.status === 401) {
        onLogout();
        return;
      }
      setError("Could not load bills");
      return;
    }
    const billData = await billResponse.json();
    setBills(billData);
  }
  async function closeBill() {
    setError("");
    const response = await apiFetch(`/bills/${year}/${month}`, {
      method: "POST",
    });
    if (!response.ok) {
      if (response.status === 401) {
        onLogout();
        return;
      }
      const data = await response.json();
      setError(data.detail);
      return;
    }
    await load();
  }

  async function pay(billId: number) {
    setError("");
    const response = await apiFetch(`/bills/${billId}/payment`, {
      method: "POST",
    });
    if (!response.ok) {
      if (response.status === 401) {
        onLogout();
        return;
      }
      const data = await response.json();
      setError(data.detail);
      return;
    }
    const data = await response.json();
    window.location.assign(data.url);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section className={cardClass}>
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-semibold">Bills</h2>
        <button className={secondaryButtonClass} onClick={closeBill}>
          Close {label}
        </button>
      </div>
      {bills.length === 0 ? (
        <p className="text-sm text-slate-500">No closed bills yet</p>
      ) : (
        <ul className="divide-y divide-slate-200">
          {bills.map((bill) => {
            const monthName = new Date(
              bill.year,
              bill.month - 1,
              1,
            ).toLocaleDateString(undefined, { month: "long", year: "numeric" });
            return (
              <li key={bill.id} className="py-2">
                <div className="flex justify-between items-center gap-3">
                  <span>
                    {monthName} · {formatMoney(bill.total, bill.currency)}
                  </span>
                  {bill.paid_at ? (
                    <span className="rounded-full bg-green-100 text-green-800 text-xs px-2 py-0.5">
                      Paid
                    </span>
                  ) : bill.total === 0 ? (
                    <span className="rounded-full bg-slate-100 text-slate-600 text-xs px-2 py-0.5">
                      Nothing to pay
                    </span>
                  ) : (
                    <button
                      className={buttonClass}
                      onClick={() => pay(bill.id)}
                    >
                      Pay
                    </button>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}
      {payment === "success" ? (
        <p className="rounded-lg bg-green-50 text-green-800 text-sm p-3 mt-3">
          Payment received — it may take a few seconds to show as paid.
        </p>
      ) : payment === "cancel" ? (
        <p className="rounded-lg bg-slate-100 text-slate-700 text-sm p-3 mt-3">
          Payment cancelled
        </p>
      ) : null}
      {error && <p className="text-red-600 text-sm mt-3">{error}</p>}
    </section>
  );
}

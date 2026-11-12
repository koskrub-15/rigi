import "chart.js/auto";

import { cardClass } from "../styles";

import type { Bill } from "../types";
import { TICKET_NAMES, formatMoney } from "../format";

export function BillView({ bill }: { bill: Bill }) {
  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold mb-3">This month</h2>
      {bill.tickets.length === 0 ? (
        <p className="text-sm text-slate-500">There are no tickets yet</p>
      ) : (
        <ul className="divide-y divide-slate-200">
          {bill.tickets.map((ticket) => {
            const validFrom = new Date(ticket.valid_from + "Z");
            return (
              <li key={ticket.type + ticket.valid_from} className="py-2">
                <div className="flex justify-between">
                  <span>{TICKET_NAMES[ticket.type]}</span>
                  <span>{formatMoney(ticket.price, bill.currency)}</span>
                </div>
                <p className="text-sm text-slate-500">
                  from{" "}
                  {validFrom.toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  })}
                </p>
              </li>
            );
          })}
        </ul>
      )}
      <p className="flex justify-between border-t border-slate-200 pt-2 mt-2 font-semibold">
        <span>Total</span>
        <span>{formatMoney(bill.total, bill.currency)}</span>
      </p>
    </section>
  );
}

import "chart.js/auto";
import { Bar } from "react-chartjs-2";

import { cardClass } from "../styles";

import type { Stats } from "../types";
import { formatMoney } from "../format";

export function StatsView({ stats }: { stats: Stats }) {
  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold mb-3">Statistics</h2>
      {stats.trips_count === 0 ? (
        <p className="text-sm text-slate-500">No trips this month</p>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Trips</p>
              <p className="text-lg font-semibold">{stats.trips_count}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Paid</p>
              <p className="text-lg font-semibold">
                {formatMoney(stats.paid, stats.currency)}
              </p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">Saved</p>
              <p className="text-lg font-semibold text-green-700">
                {formatMoney(stats.singles_price - stats.paid, stats.currency)}
              </p>
            </div>
          </div>
          <p className="mt-3 text-sm text-slate-500">
            Single tickets would cost{" "}
            {formatMoney(stats.singles_price, stats.currency)}
          </p>
          <h3 className="mt-3 mb-2 text-sm font-semibold">Trips per day</h3>
          <Bar
            data={{
              labels: stats.per_day.map((perDay) =>
                new Date(perDay.day + "T00:00").toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                }),
              ),
              datasets: [
                {
                  label: "Trips",
                  data: stats.per_day.map((perDay) => perDay.trips),
                  backgroundColor: "#2563eb",
                  borderRadius: 4,
                },
              ],
            }}
            options={{
              plugins: {
                legend: { display: false },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: { stepSize: 1 },
                },
              },
            }}
          />
        </>
      )}
    </section>
  );
}

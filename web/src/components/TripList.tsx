import "chart.js/auto";

import { cardClass } from "../styles";

import type { Trip } from "../types";
import { TIME_FORMAT } from "../format";

export function TripsList({ trips }: { trips: Trip[] }) {
  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold mb-3">Trips</h2>
      {trips.length === 0 ? (
        <p className="text-sm text-slate-500">There are no trips yet</p>
      ) : (
        <ul className="divide-y divide-slate-200">
          {trips.map((trip) => {
            const start = new Date(trip.start + "Z");
            const end = new Date(trip.end + "Z");
            return (
              <li key={trip.start} className="py-2">
                <div className="flex justify-between">
                  <span className="flex items-center gap-2">
                    <span className="font-semibold">
                      {trip.from_zone} → {trip.to_zone}
                    </span>
                    {trip.forgotten && (
                      <span className="rounded-full bg-amber-100 text-amber-800 text-xs px-2 py-0.5 whitespace-nowrap shrink-0">
                        forgotten
                      </span>
                    )}
                  </span>
                  <span>
                    {trip.zones} {trip.zones === 1 ? "zone" : "zones"}
                  </span>
                </div>
                <div className="text-sm text-slate-500">
                  <span>
                    {start.toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                    })}
                    , {start.toLocaleTimeString(undefined, TIME_FORMAT)} –{" "}
                    {end.toLocaleTimeString(undefined, TIME_FORMAT)}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

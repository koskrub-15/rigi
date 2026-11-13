import { TIME_FORMAT } from "../format";
import { cardClass } from "../styles";

import type { OpenedTrip } from "../types";

export function CurrentTrip({ trip }: { trip: OpenedTrip | null | undefined }) {
  if (trip === undefined)
    return <section className={cardClass}>Loading…</section>;
  return (
    <section className={cardClass}>
      {trip ? (
        <h2 className="text-lg font-semibold">
          On a trip since{" "}
          {new Date(trip.start + "Z").toLocaleTimeString(
            undefined,
            TIME_FORMAT,
          )}{" "}
          · Zone {trip.from_zone}
        </h2>
      ) : (
        <h2 className="text-lg font-semibold">Not on a trip</h2>
      )}
    </section>
  );
}

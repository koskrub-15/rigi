import { monthBounds } from "./month";
import { Chart } from "chart.js/auto";

const router = "http://localhost:8000/users/1";
let chart: Chart | undefined;

interface Trip {
  start: string;
  end: string;
  from_zone: string;
  to_zone: string;
  zones: number;
}

interface Ticket {
  type: string;
  valid_from: string;
  price: number;
}

interface Bill {
  tickets: Ticket[];
  total: number;
}

interface PerDay {
  day: string;
  trips: number;
}

interface Stats {
  trips_count: number;
  paid: number;
  singles_price: number;
  per_day: PerDay[];
}


async function loadTrips() {
  const response = await fetch(`${router}/trips`);
  const trips: Trip[] = await response.json();
  const list = document.querySelector("#trips")!;
  list.replaceChildren();
  for (const trip of trips) {
    const li = document.createElement("li");
    li.textContent = `${trip.start} — ${trip.end} ${trip.from_zone} -> ${trip.to_zone} \(${trip.zones} zones\)`;
    list.append(li);
  }
}


async function sendScan(scan_type: string, zone: string) {
  await fetch(`${router}/scans`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scan_type: scan_type, timestamp: new Date().toISOString(), zone: zone }) });
  await loadTrips();
  await loadBill(new Date());
  await loadStats(new Date());
}


async function loadBill(now: Date) {
  const [dateFrom, dateTo] = monthBounds(now);
  const params = new URLSearchParams({ date_from: dateFrom.toISOString(), date_to: dateTo.toISOString() });
  const response = await fetch(`${router}/bill?${params}`)
  const bill: Bill = await response.json();
  const list = document.querySelector("#bill")!;
  list.replaceChildren();
  for (const ticket of bill.tickets) {
    const li = document.createElement("li");
    li.textContent = `${ticket.type} (${ticket.valid_from}) — ${ticket.price}`;
    list.append((li));
  }
  const total = document.createElement("li");
  total.textContent = `Total: ${bill.total}`;
  list.append(total);
}


async function loadStats(now: Date) {
  // now takes a current month, but backend supports any range of dates.
  // Longer ranges are wrong, not just slow: the optimizer covers the whole
  // range at once, so a yearly "paid" is not the sum of monthly bills (947 vs 954)
  const [dateFrom, dateTo] = monthBounds(now);
  const params = new URLSearchParams({ date_from: dateFrom.toISOString(), date_to: dateTo.toISOString() });
  const response = await fetch(`${router}/stats?${params}`)
  const stats: Stats = await response.json();
  const paragraph = document.querySelector("#stats")!;
  paragraph.textContent = `Trips: ${stats.trips_count}, paid: ${stats.paid}, if use only single tickets: ${stats.singles_price}, saved: ${stats.singles_price - stats.paid}`;
  const canvas = document.querySelector<HTMLCanvasElement>("#chart")!;
  chart?.destroy();
  chart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: stats.per_day.map(d => d.day),
      datasets: [{ label: "Trips", data: stats.per_day.map(d => d.trips) }],
    },
  });

}

loadTrips();
loadBill(new Date());
loadStats(new Date());


document.querySelector("#check-in")!
  .addEventListener("click", () => sendScan(
    "check_in",
    document.querySelector<HTMLSelectElement>("#zone")!.value));
document.querySelector("#check-out")!.addEventListener("click", () => sendScan(
  "check_out",
  document.querySelector<HTMLSelectElement>("#zone")!.value));


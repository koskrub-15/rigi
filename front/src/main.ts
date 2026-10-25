import { monthBounds } from "./month";

const router = "http://localhost:8000/users/1";

interface Trip {
  start: string;
  end: string;
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


async function loadTrips() {
  const response = await fetch(`${router}/trips`);
  const trips: Trip[] = await response.json();
  const list = document.querySelector("#trips")!;
  list.replaceChildren();
  for (const trip of trips) {
    const li = document.createElement("li");
    li.textContent = `${trip.start} — ${trip.end}`;
    list.append(li);
  }
}


async function sendScan(scan_type: string) {
  await fetch(`${router}/scans`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scan_type: scan_type, timestamp: new Date().toISOString() }) });
  await loadTrips();
  await loadBill(new Date());
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



loadTrips();
loadBill(new Date());

document.querySelector("#check-in")!.addEventListener("click", () => sendScan("check_in"));
document.querySelector("#check-out")!.addEventListener("click", () => sendScan("check_out"));



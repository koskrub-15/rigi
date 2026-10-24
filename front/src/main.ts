const router = "http://localhost:8000/users/1";

interface Trip {
  start: string;
  end: string;
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
}


loadTrips();


document.querySelector("#check-in")!.addEventListener("click", () => sendScan("check_in"));
document.querySelector("#check-out")!.addEventListener("click", () => sendScan("check_out"));

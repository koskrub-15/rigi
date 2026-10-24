interface Trip {
  start: string;
  end: string;
}


async function loadTrips() {
  const response = await fetch("http://localhost:8000/users/1/trips");
  const trips: Trip[] = await response.json();
  const list = document.querySelector("#trips")!;
  list.replaceChildren();
  for (const trip of trips) {
    const li = document.createElement("li");
    li.textContent = `${trip.start} — ${trip.end}`;
    list.append(li);
  }
}

loadTrips();

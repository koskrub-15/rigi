import { useState, useEffect } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from "react-router";
import { monthBounds, previousMonth } from "./month";
import { API, apiFetch } from "./api";
import "chart.js/auto";
import { Bar } from "react-chartjs-2";
import { Scanner, type IDetectedBarcode } from "@yudiel/react-qr-scanner";

type Trip = {
  start: string;
  end: string;
  from_zone: string;
  to_zone: string;
  zones: number;
};

type Ticket = {
  type: string;
  valid_from: string;
  price: number;
};

type Bill = {
  tickets: Ticket[];
  total: number;
};

type PerDay = {
  day: string;
  trips: number;
};

type Stats = {
  trips_count: number;
  paid: number;
  singles_price: number;
  per_day: PerDay[];
};

type ClosedBill = Bill & {
  id: number;
  year: number;
  month: number;
  closed_at: string;
  paid_at: string | null;
};

const TICKET_NAMES: Record<string, string> = {
  single_ticket: "Single ticket",
  day_ticket: "Day ticket",
  weekly_ticket: "Weekly ticket",
};

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  function logout() {
    fetch(`${API}/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        refresh_token: localStorage.getItem("refresh_token"),
      }),
    });
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
  }
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            token ? (
              <>
                <Home onLogout={logout} />
                <button onClick={logout}>Log out</button>
              </>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/login"
          element={
            token ? (
              <Navigate to="/" replace />
            ) : (
              <LoginForm onLogin={setToken} />
            )
          }
        />
        <Route
          path="/register"
          element={token ? <Navigate to="/" replace /> : <RegisterForm />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const response = await fetch(`${API}/auth/login`, {
      method: "POST",
      body: new URLSearchParams({ username: email, password: password }),
    });
    if (!response.ok) {
      if (response.status === 401) setError("incorrect password or email");
      return;
    }
    const data = await response.json();
    const { access_token, refresh_token } = data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    onLogin(access_token);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        type="email"
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
      />
      <button type="submit">Submit</button>
      <p>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
      {error && <p>{error}</p>}
    </form>
  );
}

function RegisterForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const response = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        first_name: firstName,
        last_name: lastName,
        password: password,
      }),
    });
    if (!response.ok) {
      if (response.status === 409) setError("this email is already registered");
      if (response.status === 422)
        setError(
          "Check your input: Password must be at least 8 characters long, first name and last name are not empty and email must be valid",
        );
      return;
    }
    navigate("/login");
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        type="text"
        placeholder="First Name"
      />
      <input
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        type="text"
        placeholder="Last Name"
      />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        type="email"
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
      />
      <button type="submit">Submit</button>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
      {error && <p>{error}</p>}
    </form>
  );
}

function Home({ onLogout }: { onLogout: () => void }) {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [bill, setBill] = useState<Bill | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState("");

  async function load() {
    const [dateFrom, dateTo] = monthBounds(new Date());
    const params = new URLSearchParams({
      date_from: dateFrom.toISOString(),
      date_to: dateTo.toISOString(),
    });

    const tripsResponse = await apiFetch(`/trips`);
    const billResponse = await apiFetch(`/bills/preview?${params}`);
    const statsResponse = await apiFetch(`/stats?${params}`);
    if (!tripsResponse.ok) {
      if (tripsResponse.status === 401) {
        onLogout();
      }
      return;
    }
    if (!billResponse.ok) {
      if (billResponse.status === 401) {
        onLogout();
      }
      return;
    }
    if (!statsResponse.ok) {
      if (statsResponse.status === 401) {
        onLogout();
      }
      return;
    }
    const tripsData = await tripsResponse.json();
    const billData = await billResponse.json();
    const statsData = await statsResponse.json();
    setTrips(tripsData);
    setBill(billData);
    setStats(statsData);
  }

  useEffect(() => {
    load();
  }, []);

  async function scan(scanType: string, code: string) {
    setError("");
    const response = await apiFetch(`/scans`, {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({
        scan_type: scanType,
        timestamp: new Date().toISOString(),
        code: code,
      }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        onLogout();
      } else {
        setError("Failed to send scan");
      }
      return;
    }
    await load();
  }

  return (
    <>
      <ScanPanel onScan={scan} />
      <TripsList trips={trips} />
      {bill && <BillView bill={bill} />}
      <ClosedBills onLogout={onLogout} />
      {stats && <StatsView stats={stats} />}
      {error && <p>{error}</p>}
    </>
  );
}

function TripsList({ trips }: { trips: Trip[] }) {
  return trips.length === 0 ? (
    <p>There are no trips yet</p>
  ) : (
    <ul>
      {" "}
      {trips.map((trip) => (
        <li key={trip.start}>
          {new Date(trip.start + "Z").toLocaleString()} —{" "}
          {new Date(trip.end + "Z").toLocaleString()} {trip.from_zone} {"->"}{" "}
          {trip.to_zone} ({trip.zones} zones){" "}
        </li>
      ))}{" "}
    </ul>
  );
}

function ScanPanel({
  onScan,
}: {
  onScan: (scanType: string, code: string) => void;
}) {
  const [code, setCode] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");

  function handleScan(results: IDetectedBarcode[]) {
    if (results.length === 0) {
      return;
    }
    setCode(results[0].rawValue);
    setScanning(false);
  }

  function handleError() {
    setError("Camera is not available");
    setScanning(false);
  }

  function toggleScanning() {
    setError("");
    setScanning((prev) => !prev);
  }

  const noCode = code.trim() === "";

  return (
    <>
      <input value={code} onChange={(e) => setCode(e.target.value)} />
      <button disabled={noCode} onClick={() => onScan("check_in", code)}>
        Check in
      </button>
      <button disabled={noCode} onClick={() => onScan("check_out", code)}>
        Check out
      </button>
      <button onClick={toggleScanning}>
        {scanning ? "Cancel" : "Scan QR-Code"}
      </button>
      {scanning && (
        <Scanner
          onScan={handleScan}
          onError={handleError}
          formats={["qr_code"]}
        />
      )}
      {error && <p>{error}</p>}
    </>
  );
}

//
function BillView({ bill }: { bill: Bill }) {
  return bill.tickets.length === 0 ? (
    <p>There are no tickets yet</p>
  ) : (
    <>
      <ul>
        {" "}
        {bill.tickets.map((ticket) => (
          <li key={ticket.type + ticket.valid_from}>
            {TICKET_NAMES[ticket.type]} valid from{" "}
            {new Date(ticket.valid_from + "Z").toLocaleDateString()} for{" "}
            {ticket.price}{" "}
          </li>
        ))}{" "}
      </ul>
      <p>Total: {bill.total}</p>
    </>
  );
}

function StatsView({ stats }: { stats: Stats }) {
  return stats.trips_count === 0 ? (
    <p>There are no stats yet</p>
  ) : (
    <>
      <p>Trips: {stats.trips_count}</p>
      <p>Paid: {stats.paid}</p>
      <p>If use only single tickets: {stats.singles_price}</p>
      <p>Saved money: {stats.singles_price - stats.paid}</p>
      <Bar
        data={{
          labels: stats.per_day.map((perDay) => perDay.day),
          datasets: [
            {
              label: "Trips",
              data: stats.per_day.map((perDay) => perDay.trips),
            },
          ],
        }}
      />
    </>
  );
}

function ClosedBills({ onLogout }: { onLogout: () => void }) {
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
    <>
      <ul>
        {bills.map((bill) => (
          <li key={bill.id}>
            <p>
              {bill.year}-{String(bill.month).padStart(2, "0")} - {bill.total}
            </p>
            {bill.paid_at ? (
              <p>Paid</p>
            ) : bill.total === 0 ? (
              <p>Nothing to pay</p>
            ) : (
              <button onClick={() => pay(bill.id)}>Pay</button>
            )}
          </li>
        ))}
      </ul>
      <button onClick={closeBill}>Close {label}</button>
      {payment === "success" ? (
        <p>Payment received — it may take a few seconds to show as paid.</p>
      ) : payment === "cancel" ? (
        <p>Payment cancelled</p>
      ) : null}
      {error && <p>{error}</p>}
    </>
  );
}

export default App;

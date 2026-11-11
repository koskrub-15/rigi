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
  forgotten: boolean;
};

type Ticket = {
  type: string;
  valid_from: string;
  price: number;
};

type Bill = {
  tickets: Ticket[];
  total: number;
  currency: string;
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
  currency: string;
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
const TIME_FORMAT = { hour: "2-digit", minute: "2-digit" } as const;

function formatMoney(amount: number, currency: string): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
  }).format(amount);
}

const inputClass =
  "w-full border border-slate-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500";
const cardClass = "bg-white rounded-xl p-4 shadow-sm";
const secondaryButtonClass =
  "border border-slate-300 bg-white text-slate-700 rounded-lg px-4 py-2 font-medium hover:bg-slate-100";
const buttonClass =
  "bg-blue-600 text-white rounded-lg px-4 py-2 font-medium hover:bg-blue-700 disabled:opacity-50";

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
      <div className="min-h-screen bg-slate-50">
        <div className="mx-auto max-w-md p-4">
          <Routes>
            <Route
              path="/"
              element={
                token ? (
                  <>
                    <Header onLogout={logout} />
                    <Home onLogout={logout} />
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
        </div>
      </div>
    </BrowserRouter>
  );
}

function Header({ onLogout }: { onLogout: () => void }) {
  return (
    <header className="mb-6 flex items-center justify-between">
      <span className="text-xl font-semibold">Rigi</span>
      <button
        className="text-sm text-slate-600 hover:underline"
        onClick={onLogout}
      >
        Log out
      </button>
    </header>
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
    <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
      <h1 className="text-2xl font-bold">Log in</h1>
      <input
        className={inputClass}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        type="email"
        placeholder="Email"
      />
      <input
        className={inputClass}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="Password"
      />
      <button className={buttonClass} type="submit">
        Submit
      </button>
      <p>
        Don't have an account?{" "}
        <Link className="text-blue-600 underline" to="/register">
          Register
        </Link>
      </p>
      {error && <p className="text-red-600 text-sm">{error}</p>}
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
    <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
      <h1 className="text-2xl font-bold">Sign up</h1>
      <input
        className={inputClass}
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        type="text"
        placeholder="First name"
      />
      <input
        className={inputClass}
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        type="text"
        placeholder="Last name"
      />
      <input
        className={inputClass}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        type="email"
        placeholder="Email"
      />
      <input
        className={inputClass}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
        placeholder="Password"
      />
      <button className={buttonClass} type="submit">
        Submit
      </button>
      <p>
        Already have an account?{" "}
        <Link className="text-blue-600 underline" to="/login">
          Log in
        </Link>
      </p>
      {error && <p className="text-red-600 text-sm">{error}</p>}
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
        return;
      }
      const data = await response.json();
      setError(
        typeof data.detail === "string" ? data.detail : "Invalid QR code",
      );
      return;
    }
    await load();
  }

  return (
    <div className="flex flex-col gap-4">
      <ScanPanel onScan={scan} sendError={error} />
      <TripsList trips={trips} />
      {bill && <BillView bill={bill} />}
      <ClosedBills onLogout={onLogout} />
      {stats && <StatsView stats={stats} />}
    </div>
  );
}

function TripsList({ trips }: { trips: Trip[] }) {
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

function ScanPanel({
  onScan,
  sendError,
}: {
  onScan: (scanType: string, code: string) => void;
  sendError: string;
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
    <section className={cardClass}>
      <h2 className="text-lg font-semibold mb-3">Scan</h2>
      <button
        className={`${secondaryButtonClass} w-full mb-3`}
        onClick={toggleScanning}
      >
        {scanning ? "Cancel" : "Scan QR-code"}
      </button>
      {scanning && (
        <Scanner
          onScan={handleScan}
          onError={handleError}
          formats={["qr_code"]}
        />
      )}
      <input
        className={inputClass}
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <div className="flex gap-3 mt-3">
        <button
          className={`${buttonClass} flex-1`}
          disabled={noCode}
          onClick={() => onScan("check_in", code)}
        >
          Check in
        </button>
        <button
          className={`${buttonClass} flex-1`}
          disabled={noCode}
          onClick={() => onScan("check_out", code)}
        >
          Check out
        </button>
      </div>
      {sendError && <p className="text-red-600 text-sm">{sendError}</p>}
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </section>
  );
}

//
function BillView({ bill }: { bill: Bill }) {
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

function StatsView({ stats }: { stats: Stats }) {
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

export default App;

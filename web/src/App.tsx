import { useState, useEffect } from "react";
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from "react-router";

const API = "http://localhost:8000";

type Trip = {
  start: string;
  end: string;
  from_zone: string;
  to_zone: string;
  zones: number;
}


function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  function logout() {
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
                <TripsList token={token} onLogout={logout} />
                <button onClick={logout}>Log out</button>
              </>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/login" element={token ? <Navigate to="/" replace /> : <LoginForm onLogin={setToken} />} />
        <Route path="/register" element={token ? <Navigate to="/" replace /> : <RegisterForm />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
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
      body: new URLSearchParams({ username: email, password: password })
    });
    if (!response.ok) {
      if (response.status === 401)
        setError("incorrect password or email");
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
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
      <button type="submit">Submit</button>
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
      if (response.status === 409)
        setError("this email is already registered");
      if (response.status === 422)
        setError("Check your input: Password must be at least 8 characters long, first name and last name are not empty and email must be valid");
      return;
    }
    navigate("/login");
  }


  return (
    <form onSubmit={handleSubmit}>
      <input value={firstName} onChange={(e) => setFirstName(e.target.value)} type="text" placeholder="First Name" />
      <input value={lastName} onChange={(e) => setLastName(e.target.value)} type="text" placeholder="Last Name" />
      <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
      <button type="submit">Submit</button>
      <p>Already have an account? <Link to="/login">Log in</Link></p>
      {error && <p>{error}</p>}
    </form>
  )

}

function TripsList({ token, onLogout }: { token: string; onLogout: () => void }) {
  const [trips, setTrips] = useState<Trip[]>([]);

  useEffect(() => {
    async function fetchTrips() {
      const response = await fetch(`${API}/trips`, { headers: { "Authorization": `Bearer ${token}` } });
      if (!response.ok) {
        if (response.status === 401) {
          onLogout();
        }
        return;
      }
      const data = await response.json();
      setTrips(data);
    }
    fetchTrips();
  }, [token]);

  return (
    trips.length === 0 ? <p>There are no trips yet</p> : <ul> {trips.map((trip) => <li key={trip.start}>{trip.start} — {trip.end} {trip.from_zone} {"->"} {trip.to_zone} ({trip.zones} zones) </li>)} </ul>
  )
}

export default App;
